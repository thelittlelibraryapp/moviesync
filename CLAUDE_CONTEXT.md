# MovieSync - Claude Code Context File

**Created:** 2025-11-08
**Purpose:** This file contains complete context for Claude Code to continue working on MovieSync deployment.

## 🎯 Project Overview

**MovieSync** is a web application that uses audio fingerprinting (like Shazam) to identify movies from TV audio and display timestamped comments from other users.

**Tech Stack:**
- **Frontend:** React (deployed on Netlify)
- **Backend:** FastAPI/Python (deployed on Railway)
- **Database:** PostgreSQL (hosted on Supabase)
- **Audio Fingerprinting:** Chromaprint/pyacoustid

**User Flow:**
1. User opens web app and clicks "Start Listening"
2. App records 10 seconds of audio from their microphone (TV playing in background)
3. Audio is fingerprinted and matched against database
4. App displays movie title, current timestamp, and comments from other users at that timestamp
5. User can post comments that are anchored to the current timestamp

## 📁 Project Structure

```
moviesync/
├── backend/
│   ├── main.py              # FastAPI app with 4 endpoints
│   ├── fingerprint.py       # Audio fingerprinting logic
│   ├── models.py            # SQLAlchemy ORM models
│   ├── database.py          # Database connection setup
│   ├── requirements.txt     # Python dependencies
│   ├── runtime.txt          # Python 3.11.0
│   ├── Procfile            # Railway deployment config
│   └── README.md           # Backend documentation
├── frontend/
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── App.js          # Main component (listening vs feed state)
│   │   ├── ListeningState.js   # Recording UI
│   │   ├── CommentFeed.js      # Comments display and posting
│   │   ├── AudioRecorder.js    # Web Audio API recording
│   │   ├── api.js              # Backend API client
│   │   └── App.css             # Mobile-first dark theme
│   ├── package.json
│   ├── .env.example
│   └── README.md
├── tools/
│   ├── extract_audio.py         # FFmpeg audio extraction
│   ├── fingerprint_movie.py     # Generate fingerprints
│   ├── process_all_movies.sh    # Batch processing
│   ├── requirements.txt         # Tool dependencies
│   └── README.md
├── database/
│   └── schema.sql          # PostgreSQL schema + 10 movie seeds
├── README.md               # Project overview
└── DEPLOYMENT.md           # Deployment guide
```

## 🚀 Current Deployment Status

### ✅ Completed
1. **Code Complete** - All 30 files created and tested locally
2. **Git Repository** - Code pushed to https://github.com/thelittlelibraryapp/moviesync
3. **Railway Deployment Started** - Backend connected to Railway
4. **SQLAlchemy Fix Applied** - Updated to `sqlalchemy>=2.0.36` for Python 3.14 compatibility

### 🔧 In Progress
- **Railway Backend Deployment** - Waiting for auto-redeploy after SQLAlchemy fix
- **Supabase Database** - Not yet created

### ⏳ Pending
- Setup Supabase PostgreSQL database
- Run schema.sql to create tables and seed movies
- Deploy frontend to Netlify
- Configure environment variables
- Update CORS settings
- End-to-end testing
- (Optional) Process movie audio files to generate fingerprints

## 🐛 Recent Issues & Fixes

### Issue 1: SQLAlchemy/Python 3.14 Compatibility ✅ FIXED
**Problem:** Railway deployment failing with:
```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'>
directly inherits TypingOnly but has additional attributes
```

**Root Cause:** Railway using Python 3.14.0, but SQLAlchemy 2.0.23 doesn't support it

**Fix Applied:** Updated `backend/requirements.txt:3`
```diff
- sqlalchemy==2.0.23
+ sqlalchemy>=2.0.36
```

**Status:** Fix pushed to git, Railway auto-redeploy in progress

## 📋 Detailed Next Steps

### Step 1: Verify Railway Backend Deployment

1. Check Railway logs - should show successful startup
2. Expected log output:
   ```
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```
3. Note the Railway public URL (e.g., `https://moviesynk-backend-production.up.railway.app`)

### Step 2: Setup Supabase Database (10 minutes)

1. Go to https://supabase.com and create account
2. Create new project:
   - Project name: "MovieSync"
   - Database password: [generate strong password - save it!]
   - Region: Choose closest to your users
3. Wait 2-3 minutes for project provisioning
4. Go to SQL Editor in Supabase dashboard
5. Copy entire contents of `database/schema.sql`
6. Paste into SQL Editor and click "Run"
7. Verify tables created:
   - Go to Table Editor
   - Should see: movies (10 rows), fingerprints (0 rows), comments (0 rows)
8. Get connection string:
   - Go to Project Settings → Database
   - Copy "Connection string" under "Connection pooling"
   - Format: `postgresql://postgres:[password]@[host]:6543/postgres`
9. Add DATABASE_URL to Railway:
   - Go to Railway project → Variables
   - Add: `DATABASE_URL=postgresql://postgres:...`
   - Redeploy will trigger automatically

### Step 3: Deploy Frontend to Netlify (10 minutes)

1. Go to https://netlify.com and create account
2. Click "Add new site" → "Import an existing project"
3. Connect to GitHub and select `moviesync` repository
4. Configure build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`
5. Add environment variable:
   - Key: `REACT_APP_API_URL`
   - Value: [Your Railway URL from Step 1]
6. Click "Deploy site"
7. Wait 2-3 minutes for deployment
8. Note the Netlify URL (e.g., `https://moviesynk-abc123.netlify.app`)

### Step 4: Update CORS Settings

1. Edit `backend/main.py`
2. Update CORS origins to include your Netlify URL:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "https://moviesynk-abc123.netlify.app"  # Add this
       ],
       ...
   )
   ```
3. Commit and push - Railway will auto-redeploy

### Step 5: Test End-to-End

1. Open Netlify URL in browser
2. Click "Start Listening"
3. Grant microphone permission
4. Play a movie from the seeded list (see below)
5. App should match the movie and show timestamp
6. Post a test comment
7. Refresh - comment should appear

### Step 6 (Optional): Generate Movie Fingerprints (2-4 hours)

**Note:** This requires movie files on your local machine. Skip if you just want to test the app.

1. Obtain video files for the 10 seeded movies (see list below)
2. Install Python dependencies: `pip install -r tools/requirements.txt`
3. Install FFmpeg: https://ffmpeg.org/download.html
4. Create `.env` in tools directory with DATABASE_URL
5. For each movie:
   ```bash
   python tools/extract_audio.py "movie.mp4" "movie.wav"
   python tools/fingerprint_movie.py "movie.wav" [movie_id]
   ```
6. Or use batch script: `bash tools/process_all_movies.sh`
7. Each movie takes 15-30 minutes to process

## 🎬 Seeded Movies (IDs 1-10)

1. The Shawshank Redemption (1994) - 142 min
2. The Godfather (1972) - 175 min
3. The Dark Knight (2008) - 152 min
4. Pulp Fiction (1994) - 154 min
5. Forrest Gump (1994) - 142 min
6. Inception (2010) - 148 min
7. The Matrix (1999) - 136 min
8. Goodfellas (1990) - 145 min
9. The Silence of the Lambs (1991) - 118 min
10. Saving Private Ryan (1998) - 169 min

## 🔑 Environment Variables Reference

### Railway Backend
```
DATABASE_URL=postgresql://postgres:[password]@[host]:6543/postgres
```

### Netlify Frontend
```
REACT_APP_API_URL=https://your-backend.up.railway.app
```

### Local Tools (Optional)
```
DATABASE_URL=postgresql://postgres:[password]@[host]:6543/postgres
```

## 🏗️ Technical Architecture

### Backend API Endpoints

1. **POST /api/match**
   - Receives: Base64-encoded WAV audio (10 seconds, 16kHz mono)
   - Returns: Movie match with title, year, timestamp, confidence
   - Logic: Generates Chromaprint fingerprint, compares with database (80% threshold)

2. **GET /api/comments?movie_id={id}&timestamp={sec}&window={sec}**
   - Returns: Comments within ±window seconds of timestamp
   - Default window: 30 seconds

3. **POST /api/comment**
   - Receives: movie_id, timestamp_seconds, username, text
   - Validation: username ≤50 chars, text ≤280 chars
   - Returns: Created comment with formatted timestamp

4. **GET /api/movies**
   - Returns: List of all movies with ID, title, year, runtime

### Database Schema

**movies** table:
- id (PK), title, year, runtime_minutes, created_at

**fingerprints** table:
- id (PK), movie_id (FK), timestamp_seconds, fingerprint_data, created_at
- Index on (movie_id, timestamp_seconds) for fast lookups

**comments** table:
- id (PK), movie_id (FK), timestamp_seconds, username, text, created_at
- Index on (movie_id, timestamp_seconds)

### Audio Processing

1. **Recording:** Web Audio API captures 10 seconds at 16kHz mono
2. **Encoding:** Converted to WAV format, base64 encoded
3. **Transmission:** Sent to backend via POST /api/match
4. **Fingerprinting:** Backend uses pyacoustid (Chromaprint) to generate fingerprint
5. **Matching:** Compares against database fingerprints, returns best match >80% confidence
6. **Timestamp Calculation:** Uses offset_seconds from matching fingerprint

### Frontend State Management

- **App.js:** Controls view state ('listening' vs 'feed')
- **ListeningState.js:** Manages recording, processing, error states
- **CommentFeed.js:** Manages comments list, post form, auto-refresh (10s interval)
- **AudioRecorder.js:** Encapsulates Web Audio API logic

## 🔍 Important Files to Know

### backend/fingerprint.py
Contains core matching logic:
- `generate_fingerprint(audio_bytes)`: Creates Chromaprint fingerprint
- `match_fingerprint(fingerprint, db_session)`: Finds best match in database
- Threshold: 80% similarity required for match

### frontend/src/AudioRecorder.js
Web Audio API implementation:
- Records at 16kHz, mono, 16-bit
- Converts to WAV format
- Returns base64 string for API transmission

### database/schema.sql
Complete schema with:
- Table definitions with indexes
- 10 classic movie seeds
- Proper foreign key constraints

## 🚨 Common Issues & Solutions

### Issue: "No module named 'chromaprint'"
**Solution:** Install chromaprint library:
- macOS: `brew install chromaprint`
- Ubuntu: `apt-get install libchromaprint-dev`
- Windows: Download from https://acoustid.org/chromaprint

### Issue: CORS errors in browser
**Solution:** Ensure Netlify URL is in CORS origins list in `backend/main.py`

### Issue: "No match found"
**Solution:**
- Ensure movie is from the seeded list (IDs 1-10)
- Ensure fingerprints have been generated for that movie
- Check audio quality - needs clear movie audio (not too much background noise)
- Verify database connection is working

### Issue: Railway deployment timeout
**Solution:**
- Check Railway logs for specific errors
- Verify DATABASE_URL is set correctly
- Ensure requirements.txt has all dependencies
- Check Python version compatibility (runtime.txt)

## 📝 Git Workflow Notes

**Main branch:** `main` (or `master` - check with `git branch`)

**Current working branch:** `claude/build-moviesync-app-011CUuZ6zmuZFh1JPtEJERjV`

**For new Claude Code session:**
- Work directly on `main` branch OR
- Create new feature branch: `claude/moviesync-deployment-[session-id]`

## 🎯 Success Criteria

The deployment is complete when:
1. ✅ Railway backend shows "Deployment successful" and responds to /api/movies
2. ✅ Supabase database has 3 tables with 10 movies seeded
3. ✅ Netlify frontend is live and loads without errors
4. ✅ Can record audio and see "processing" state
5. ✅ Can post and view comments (even if no fingerprints yet)
6. ⚠️ Movie matching works (requires fingerprint generation - optional)

## 💡 Tips for Claude Code

1. **Check Railway logs first** - Most backend issues show up in logs
2. **Test API endpoints** - Use `curl` or browser to verify backend works
3. **Frontend .env** - Must be set before `npm run build` (not after)
4. **Database connection** - Use connection pooling URL (port 6543, not 5432)
5. **CORS is critical** - Frontend won't work without proper CORS config
6. **Microphone permission** - Requires HTTPS in production (Netlify provides this)

## 📞 Current Status Summary

**Last commit:** Fix SQLAlchemy compatibility with Python 3.14 (commit 550bc71)

**Waiting on:**
- Railway auto-redeploy to complete
- User to verify deployment successful

**Ready to do next:**
- Setup Supabase database (Step 2)
- Deploy frontend to Netlify (Step 3)

---

## 🤖 Instructions for Next Claude Code Session

1. Read this entire file to understand the project
2. Ask user: "Which step are we on? Has Railway deployment succeeded?"
3. Based on their answer, continue from the appropriate step above
4. Use the reference information as needed
5. When creating commits, use clear messages referencing what step you're on

**Good first message:**
"I've read the context file. I can see we've fixed the SQLAlchemy issue and are waiting for Railway to redeploy. What's the current status? Has the Railway deployment succeeded?"
