"""
SQLAlchemy database models for MovieSync.
Defines the structure for movies, fingerprints, and comments tables.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Movie(Base):
    """Movie model - stores basic movie information."""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    runtime_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        """Convert movie to dictionary for JSON responses."""
        hours = self.runtime_seconds // 3600
        minutes = (self.runtime_seconds % 3600) // 60
        seconds = self.runtime_seconds % 60
        runtime_formatted = f"{hours}:{minutes:02d}:{seconds:02d}"

        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "runtime_seconds": self.runtime_seconds,
            "runtime_formatted": runtime_formatted
        }


class Fingerprint(Base):
    """Fingerprint model - stores Chromaprint audio fingerprints."""
    __tablename__ = "fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    timestamp_seconds = Column(Integer, nullable=False)
    fingerprint_data = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Comment(Base):
    """Comment model - stores user comments at specific movie timestamps."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    timestamp_seconds = Column(Integer, nullable=False)
    username = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        """Convert comment to dictionary for JSON responses."""
        minutes = self.timestamp_seconds // 60
        seconds = self.timestamp_seconds % 60
        timestamp_formatted = f"{minutes}:{seconds:02d}"

        return {
            "id": self.id,
            "username": self.username,
            "text": self.text,
            "timestamp_seconds": self.timestamp_seconds,
            "timestamp_formatted": timestamp_formatted,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
