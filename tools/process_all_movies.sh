#!/bin/bash

# MovieSync - Process All Movies
# Batch script to extract audio and generate fingerprints for all 10 movies

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    echo "Please create a .env file with DATABASE_URL"
    exit 1
fi

# Check DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL not set in .env file"
    exit 1
fi

# Create audio output directory
mkdir -p audio

# Movie list: "filename:movie_id:title"
MOVIES=(
  "The_Shawshank_Redemption.mp4:1:The Shawshank Redemption"
  "The_Godfather.mp4:2:The Godfather"
  "The_Dark_Knight.mkv:3:The Dark Knight"
  "Pulp_Fiction.mp4:4:Pulp Fiction"
  "Forrest_Gump.mp4:5:Forrest Gump"
  "The_Matrix.mp4:6:The Matrix"
  "Inception.mkv:7:Inception"
  "Goodfellas.mp4:8:Goodfellas"
  "Fight_Club.mp4:9:Fight Club"
  "Interstellar.mkv:10:Interstellar"
)

echo "========================================="
echo "MovieSync - Processing All Movies"
echo "========================================="
echo ""

# Track statistics
TOTAL_MOVIES=${#MOVIES[@]}
PROCESSED=0
FAILED=0

for entry in "${MOVIES[@]}"; do
  IFS=':' read -r filename movie_id title <<< "$entry"

  echo "Processing: $title"
  echo "File: $filename"
  echo "Movie ID: $movie_id"
  echo "-----------------------------------------"

  # Check if movie file exists
  if [ ! -f "movies/$filename" ]; then
    echo "❌ Error: movies/$filename not found"
    echo "Please add this file to the movies/ directory"
    echo ""
    FAILED=$((FAILED + 1))
    continue
  fi

  # Extract audio
  echo "Step 1/2: Extracting audio..."
  python3 extract_audio.py \
    --input "movies/$filename" \
    --output "audio/movie_${movie_id}.wav"

  if [ $? -ne 0 ]; then
    echo "❌ Error extracting audio from $filename"
    echo ""
    FAILED=$((FAILED + 1))
    continue
  fi

  # Generate fingerprints
  echo "Step 2/2: Generating fingerprints..."
  python3 fingerprint_movie.py \
    --audio "audio/movie_${movie_id}.wav" \
    --movie-id $movie_id \
    --database-url "$DATABASE_URL"

  if [ $? -ne 0 ]; then
    echo "❌ Error generating fingerprints for $filename"
    echo ""
    FAILED=$((FAILED + 1))
    continue
  fi

  echo "✓ Completed: $title"
  echo ""
  PROCESSED=$((PROCESSED + 1))
done

echo "========================================="
echo "Processing Complete!"
echo "========================================="
echo ""
echo "Total movies: $TOTAL_MOVIES"
echo "Successfully processed: $PROCESSED"
echo "Failed: $FAILED"
echo ""

if [ $PROCESSED -gt 0 ]; then
  echo "Database now contains fingerprints for $PROCESSED movie(s)."
  echo "You can now run the MovieSync app."
fi

if [ $FAILED -gt 0 ]; then
  echo ""
  echo "Note: $FAILED movie(s) failed to process."
  echo "Check the errors above for details."
  exit 1
fi

exit 0
