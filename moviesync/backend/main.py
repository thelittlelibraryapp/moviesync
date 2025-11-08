"""
MovieSync FastAPI Backend
Provides API endpoints for audio fingerprinting and comment management.
"""

import os
import re
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db
from models import Movie, Comment
from fingerprint import decode_base64_audio, generate_fingerprint, match_fingerprint

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="MovieSync API", version="1.0.0")

# Configure CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class MatchRequest(BaseModel):
    """Request model for audio matching endpoint."""
    audio: str = Field(..., description="Base64 encoded WAV audio data")


class CommentRequest(BaseModel):
    """Request model for posting a comment."""
    movie_id: int = Field(..., gt=0, description="Movie ID")
    timestamp_seconds: int = Field(..., ge=0, description="Timestamp in seconds")
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    text: str = Field(..., min_length=1, max_length=280, description="Comment text")

    @validator('username')
    def validate_username(cls, v):
        """Validate username contains only alphanumeric characters, underscores, and hyphens."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v


# Helper Functions
def format_timestamp(seconds: int) -> str:
    """Format seconds as MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def time_ago(dt: datetime) -> str:
    """Calculate human-readable time ago string."""
    now = datetime.utcnow()
    if dt.tzinfo:
        # Make now timezone-aware if dt is timezone-aware
        from datetime import timezone
        now = datetime.now(timezone.utc)

    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"


# API Endpoints
@app.get("/")
def root():
    """Root endpoint - API health check."""
    return {
        "service": "MovieSync API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/match")
def match_audio(request: MatchRequest, db: Session = Depends(get_db)):
    """
    Identify movie and timestamp from audio clip.

    Accepts base64 encoded WAV audio, generates fingerprint,
    and matches against database to identify movie and timestamp.
    """
    try:
        # Decode base64 audio
        audio_bytes = decode_base64_audio(request.audio)
        if not audio_bytes:
            return {
                "success": False,
                "error": "Invalid audio data. Please ensure audio is properly encoded."
            }

        # Generate fingerprint
        fingerprint = generate_fingerprint(audio_bytes)
        if not fingerprint:
            return {
                "success": False,
                "error": "Could not process audio. Please try recording again closer to your TV speakers."
            }

        # Match against database
        match = match_fingerprint(fingerprint, db)
        if not match:
            return {
                "success": False,
                "error": "No matching movie found. Try recording closer to your TV speakers or ensure you're watching one of the supported movies."
            }

        # Return match details
        return {
            "success": True,
            "movie_id": match["movie_id"],
            "title": match["title"],
            "year": match["year"],
            "timestamp_seconds": match["timestamp"],
            "timestamp_formatted": format_timestamp(match["timestamp"]),
            "confidence": round(match["confidence"], 2)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred while processing your audio: {str(e)}"
        }


@app.get("/api/comments")
def get_comments(
    movie_id: int,
    timestamp: int,
    window: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get comments near a timestamp.

    Returns comments within a time window around the specified timestamp.
    """
    try:
        # Validate movie exists
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return {
                "success": False,
                "error": "Movie not found"
            }

        # Calculate window boundaries
        half_window = window // 2
        window_start = max(0, timestamp - half_window)
        window_end = min(movie.runtime_seconds, timestamp + half_window)

        # Query comments in window
        comments = db.query(Comment).filter(
            Comment.movie_id == movie_id,
            Comment.timestamp_seconds >= window_start,
            Comment.timestamp_seconds <= window_end
        ).order_by(Comment.created_at.desc()).limit(100).all()

        # Format comments
        formatted_comments = []
        for comment in comments:
            comment_dict = comment.to_dict()
            comment_dict["time_ago"] = time_ago(comment.created_at)
            formatted_comments.append(comment_dict)

        return {
            "success": True,
            "comments": formatted_comments,
            "total": len(formatted_comments),
            "window_start": window_start,
            "window_end": window_end
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving comments: {str(e)}"
        }


@app.post("/api/comment", status_code=status.HTTP_201_CREATED)
def post_comment(request: CommentRequest, db: Session = Depends(get_db)):
    """
    Save a new comment.

    Creates a new comment at the specified movie timestamp.
    """
    try:
        # Validate movie exists
        movie = db.query(Movie).filter(Movie.id == request.movie_id).first()
        if not movie:
            return {
                "success": False,
                "error": "Movie not found"
            }

        # Validate timestamp is within movie runtime
        if request.timestamp_seconds < 0 or request.timestamp_seconds > movie.runtime_seconds:
            return {
                "success": False,
                "error": f"Timestamp must be between 0 and {movie.runtime_seconds} seconds"
            }

        # Create comment
        comment = Comment(
            movie_id=request.movie_id,
            timestamp_seconds=request.timestamp_seconds,
            username=request.username,
            text=request.text
        )

        db.add(comment)
        db.commit()
        db.refresh(comment)

        return {
            "success": True,
            "comment_id": comment.id,
            "message": "Comment posted successfully"
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": f"Error posting comment: {str(e)}"
        }


@app.get("/api/movies")
def get_movies(db: Session = Depends(get_db)):
    """
    List all available movies.

    Returns all movies in the database with their details.
    """
    try:
        movies = db.query(Movie).all()
        return {
            "success": True,
            "movies": [movie.to_dict() for movie in movies]
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving movies: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
