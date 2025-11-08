# MovieSync Audio Processing Tools

Command-line tools for processing movie audio files and generating fingerprints.

## Overview

These tools run locally (not deployed) to populate the database with audio fingerprints from your movie collection.

## Prerequisites

### System Dependencies

**FFmpeg** (for audio extraction):
```bash
# Mac
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**Chromaprint** (for fingerprinting):
```bash
# Mac
brew install chromaprint

# Ubuntu/Debian
sudo apt install libchromaprint-tools

# Windows
# Download from https://acoustid.org/chromaprint
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

## Tools

### 1. extract_audio.py

Extract audio track from video file and convert to WAV.

**Usage:**
```bash
python extract_audio.py --input "movies/The_Godfather.mp4" --output "audio/godfather.wav"
```

### 2. fingerprint_movie.py

Generate Chromaprint fingerprints and store in database.

**Usage:**
```bash
python fingerprint_movie.py \
  --audio "audio/godfather.wav" \
  --movie-id 2 \
  --database-url "postgresql://..."
```

### 3. process_all_movies.sh

Batch process all 10 movies at once.

**Usage:**
```bash
chmod +x process_all_movies.sh
./process_all_movies.sh
```

## License

MIT
