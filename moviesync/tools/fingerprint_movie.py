#!/usr/bin/env python3
"""
Generate Chromaprint fingerprints from audio file and store in database.
Processes audio in overlapping windows and stores fingerprints in Supabase.
"""

import argparse
import sys
import io
from pathlib import Path
from datetime import datetime
import acoustid
from pydub import AudioSegment
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm


def generate_fingerprint_from_segment(audio_segment):
    """
    Generate Chromaprint fingerprint from audio segment.

    Args:
        audio_segment: pydub AudioSegment

    Returns:
        Fingerprint string or None
    """
    try:
        # Convert segment to mono 16kHz
        audio = audio_segment.set_channels(1).set_frame_rate(16000)

        # Export to temporary WAV
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        # Generate fingerprint
        duration, fingerprint = acoustid.fingerprint_file(wav_io)
        return fingerprint

    except Exception as e:
        print(f"Error generating fingerprint: {e}")
        return None


def process_audio_file(audio_path, movie_id, database_url):
    """
    Process audio file and store fingerprints in database.

    Args:
        audio_path: Path to WAV audio file
        movie_id: Movie ID from database
        database_url: PostgreSQL connection string

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load audio file
        print(f"Loading audio file: {audio_path}")
        audio = AudioSegment.from_wav(str(audio_path))
        duration_seconds = len(audio) / 1000

        print(f"Audio duration: {int(duration_seconds)} seconds")
        print(f"Processing with 10-second windows, 1-second stride...")

        # Connect to database
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Delete existing fingerprints for this movie
        print(f"Deleting existing fingerprints for movie {movie_id}...")
        session.execute(
            text("DELETE FROM fingerprints WHERE movie_id = :movie_id"),
            {"movie_id": movie_id}
        )
        session.commit()

        # Process audio in 10-second windows with 1-second overlap
        window_size_ms = 10000  # 10 seconds
        stride_ms = 1000         # 1 second shift

        fingerprints = []
        num_windows = int((len(audio) - window_size_ms) / stride_ms) + 1

        print(f"Generating {num_windows} fingerprints...")

        for i in tqdm(range(num_windows), desc="Processing", unit="segment"):
            start_ms = i * stride_ms
            end_ms = start_ms + window_size_ms

            # Check if we've reached the end
            if end_ms > len(audio):
                break

            # Extract segment
            segment = audio[start_ms:end_ms]

            # Generate fingerprint
            fingerprint = generate_fingerprint_from_segment(segment)

            if fingerprint:
                timestamp_seconds = start_ms // 1000
                fingerprints.append({
                    'movie_id': movie_id,
                    'timestamp_seconds': timestamp_seconds,
                    'fingerprint_data': fingerprint
                })

                # Batch insert every 1000 fingerprints
                if len(fingerprints) >= 1000:
                    session.execute(
                        text("""
                            INSERT INTO fingerprints (movie_id, timestamp_seconds, fingerprint_data)
                            VALUES (:movie_id, :timestamp_seconds, :fingerprint_data)
                        """),
                        fingerprints
                    )
                    session.commit()
                    fingerprints = []

        # Insert remaining fingerprints
        if fingerprints:
            session.execute(
                text("""
                    INSERT INTO fingerprints (movie_id, timestamp_seconds, fingerprint_data)
                    VALUES (:movie_id, :timestamp_seconds, :fingerprint_data)
                """),
                fingerprints
            )
            session.commit()

        # Get total count
        result = session.execute(
            text("SELECT COUNT(*) FROM fingerprints WHERE movie_id = :movie_id"),
            {"movie_id": movie_id}
        )
        total_count = result.scalar()

        print(f"\n✓ Generated {total_count} fingerprints")
        print(f"✓ Stored in database")
        print(f"✓ Processing complete")

        session.close()
        return True

    except Exception as e:
        print(f"Error processing audio file: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate fingerprints from audio file and store in database'
    )
    parser.add_argument(
        '--audio',
        required=True,
        help='Path to WAV audio file'
    )
    parser.add_argument(
        '--movie-id',
        type=int,
        required=True,
        help='Movie ID from database (1-10)'
    )
    parser.add_argument(
        '--database-url',
        required=True,
        help='PostgreSQL connection string (from Supabase)'
    )

    args = parser.parse_args()

    # Validate audio file
    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)

    # Validate movie ID
    if args.movie_id < 1 or args.movie_id > 10:
        print("Warning: Movie ID should be between 1-10")

    print("=" * 60)
    print(f"MovieSync Fingerprint Generator")
    print("=" * 60)
    print(f"Movie ID: {args.movie_id}")
    print(f"Audio file: {audio_path.name}")
    print("=" * 60)
    print()

    # Process audio file
    success = process_audio_file(audio_path, args.movie_id, args.database_url)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
