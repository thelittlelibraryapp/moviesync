# MovieSync Backend

FastAPI backend for MovieSync audio fingerprinting and comment management.

## Features

- Audio fingerprinting using Chromaprint
- Movie identification from audio clips
- Timestamped comment management
- PostgreSQL database integration (Supabase)
- RESTful API

## API Endpoints

### POST /api/match
Identify movie and timestamp from audio clip.

**Request:**
```json
{
  "audio": "base64_encoded_wav_audio"
}
```

**Response:**
```json
{
  "success": true,
  "movie_id": 2,
  "title": "The Godfather",
  "year": 1972,
  "timestamp_seconds": 2145,
  "timestamp_formatted": "35:45",
  "confidence": 0.94
}
```

### GET /api/comments
Get comments near a timestamp.

**Query Parameters:**
- `movie_id` (required): Movie ID
- `timestamp` (required): Timestamp in seconds
- `window` (optional): Time window in seconds (default: 30)

**Response:**
```json
{
  "success": true,
  "comments": [...],
  "total": 47,
  "window_start": 2130,
  "window_end": 2160
}
```

### POST /api/comment
Post a new comment.

**Request:**
```json
{
  "movie_id": 2,
  "timestamp_seconds": 2145,
  "username": "MovieBuff23",
  "text": "Best scene ever!"
}
```

**Response:**
```json
{
  "success": true,
  "comment_id": 124,
  "message": "Comment posted successfully"
}
```

### GET /api/movies
List all available movies.

**Response:**
```json
{
  "success": true,
  "movies": [...]
}
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your Supabase DATABASE_URL
```

3. Run the server:
```bash
uvicorn main:app --reload
```

4. API will be available at `http://localhost:8000`

## Deployment to Railway

1. Push code to GitHub
2. Create new project in Railway
3. Connect GitHub repository
4. Add environment variables:
   - `DATABASE_URL`: Supabase connection string
   - `CORS_ORIGINS`: Your frontend URL
5. Railway auto-deploys

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `PORT`: Server port (default: 8000)

## Dependencies

- FastAPI: Web framework
- SQLAlchemy: ORM
- PostgreSQL: Database
- pyacoustid: Audio fingerprinting
- pydub: Audio processing

## License

MIT
