#!/usr/bin/env python3
"""
Extract audio from video file and convert to WAV format.
Uses FFmpeg to extract and convert audio to 16kHz mono WAV.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_duration(input_path):
    """Get video duration in seconds using ffprobe."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(input_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        print(f"Warning: Could not get video duration: {e}")
        return None


def extract_audio(input_path, output_path):
    """
    Extract audio from video file and convert to WAV.

    Args:
        input_path: Path to input video file
        output_path: Path to output WAV file

    Returns:
        True if successful, False otherwise
    """
    try:
        # FFmpeg command to extract audio
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',      # Mono channel
            '-y',            # Overwrite output file
            str(output_path)
        ]

        print(f"Extracting audio from {input_path.name}...")
        print(f"Output: {output_path}")

        # Run FFmpeg
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
            print(f"Error: FFmpeg failed with return code {process.returncode}")
            print(f"Error output: {process.stderr}")
            return False

        # Check output file exists and has size
        if not output_path.exists():
            print("Error: Output file was not created")
            return False

        file_size_mb = output_path.stat().st_size / (1024 * 1024)

        # Get duration
        duration = get_video_duration(input_path)
        duration_str = ""
        if duration:
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            duration_str = f"{hours}:{minutes:02d}:{seconds:02d} ({int(duration)} seconds)"

        print(f"✓ Successfully extracted audio")
        print(f"✓ Saved to {output_path}")
        if duration_str:
            print(f"✓ Duration: {duration_str}")
        print(f"✓ File size: {file_size_mb:.1f} MB")

        return True

    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Extract audio from video file and convert to WAV'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input video file (MP4, MKV, AVI, MOV, etc.)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path for output WAV file'
    )

    args = parser.parse_args()

    # Check FFmpeg is installed
    if not check_ffmpeg():
        print("Error: FFmpeg is not installed or not in PATH")
        print("\nPlease install FFmpeg:")
        print("  Mac:     brew install ffmpeg")
        print("  Ubuntu:  sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Extract audio
    success = extract_audio(input_path, output_path)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
