"""
Audio fingerprinting and matching logic for MovieSync.
Uses Chromaprint/pyacoustid for generating and comparing audio fingerprints.
"""

import base64
import io
import logging
from typing import Optional, Dict
import acoustid
from pydub import AudioSegment
from sqlalchemy.orm import Session
from models import Fingerprint, Movie

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Matching threshold (80% similarity required)
MATCH_THRESHOLD = 0.80


def generate_fingerprint(audio_bytes: bytes) -> Optional[str]:
    """
    Generate Chromaprint fingerprint from audio data.

    Args:
        audio_bytes: Raw audio data (WAV format)

    Returns:
        Fingerprint string or None if generation fails
    """
    try:
        # Convert bytes to AudioSegment
        audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))

        # Convert to mono 16kHz (Chromaprint requirements)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)

        # Export to temporary WAV for acoustid processing
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        # Generate fingerprint using acoustid
        duration, fingerprint = acoustid.fingerprint_file(wav_io)

        logger.info(f"Generated fingerprint (duration: {duration}s)")
        return fingerprint

    except Exception as e:
        logger.error(f"Error generating fingerprint: {str(e)}")
        return None


def calculate_similarity(fp1: str, fp2: str) -> float:
    """
    Calculate similarity between two fingerprints.

    Args:
        fp1: First fingerprint string
        fp2: Second fingerprint string

    Returns:
        Similarity score from 0.0 to 1.0
    """
    try:
        # Simple string similarity for MVP
        # In production, use proper Chromaprint comparison
        if fp1 == fp2:
            return 1.0

        # Compare fingerprint substrings
        # Chromaprint fingerprints can be compared by finding common sequences
        min_len = min(len(fp1), len(fp2))
        max_len = max(len(fp1), len(fp2))

        if max_len == 0:
            return 0.0

        # Count matching characters in overlapping region
        matches = sum(1 for i in range(min_len) if fp1[i] == fp2[i])
        similarity = matches / max_len

        return similarity

    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        return 0.0


def match_fingerprint(fingerprint: str, db_session: Session) -> Optional[Dict]:
    """
    Match incoming fingerprint against database fingerprints.

    Args:
        fingerprint: Fingerprint string to match
        db_session: Database session

    Returns:
        Dictionary with match details or None if no good match found:
        {
            "movie_id": int,
            "title": str,
            "year": int,
            "timestamp": int,
            "confidence": float
        }
    """
    try:
        # Get all fingerprints from database
        all_fingerprints = db_session.query(Fingerprint).all()

        if not all_fingerprints:
            logger.warning("No fingerprints in database")
            return None

        logger.info(f"Comparing against {len(all_fingerprints)} fingerprints")

        # Find best match
        best_match = None
        best_similarity = 0.0

        for fp in all_fingerprints:
            similarity = calculate_similarity(fingerprint, fp.fingerprint_data)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = fp

        # Check if best match meets threshold
        if best_similarity < MATCH_THRESHOLD:
            logger.info(f"Best match similarity {best_similarity:.2f} below threshold {MATCH_THRESHOLD}")
            return None

        # Get movie details
        movie = db_session.query(Movie).filter(Movie.id == best_match.movie_id).first()

        if not movie:
            logger.error(f"Movie {best_match.movie_id} not found")
            return None

        logger.info(f"Match found: {movie.title} at {best_match.timestamp_seconds}s (confidence: {best_similarity:.2f})")

        return {
            "movie_id": movie.id,
            "title": movie.title,
            "year": movie.year,
            "timestamp": best_match.timestamp_seconds,
            "confidence": best_similarity
        }

    except Exception as e:
        logger.error(f"Error matching fingerprint: {str(e)}")
        return None


def decode_base64_audio(base64_string: str) -> Optional[bytes]:
    """
    Decode base64 encoded audio data.

    Args:
        base64_string: Base64 encoded audio

    Returns:
        Audio bytes or None if decoding fails
    """
    try:
        audio_bytes = base64.b64decode(base64_string)
        return audio_bytes
    except Exception as e:
        logger.error(f"Error decoding base64 audio: {str(e)}")
        return None
