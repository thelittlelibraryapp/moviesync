# 🎬 MovieSync

> Audio fingerprinting app for timestamped movie comments

Point your phone at your TV, identify the movie and exact moment, then see what everyone else is thinking at that same timestamp.

## ✨ Features

- 🎵 **Audio fingerprinting** (like Shazam for movies)
- 💬 **Timestamped comments** on any moment
- 📱 **Works on any device** with a browser
- 🎭 **Platform-agnostic** (Netflix, Prime, DVD, theaters, etc.)
- 🎯 **Currently supports** 10 greatest movies of all time

## 🎥 Supported Movies

1. The Shawshank Redemption (1994)
2. The Godfather (1972)
3. The Dark Knight (2008)
4. Pulp Fiction (1994)
5. Forrest Gump (1994)
6. The Matrix (1999)
7. Inception (2010)
8. Goodfellas (1990)
9. Fight Club (1999)
10. Interstellar (2014)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+
- FFmpeg (for audio processing)
- Chromaprint (for fingerprinting)
- Supabase account (free tier)
- Railway account (free tier)
- Netlify account (free tier)

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Supabase DATABASE_URL
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with backend URL
npm start
```

### Full Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step deployment instructions.

## 🏗️ Architecture

```
┌─────────────┐      HTTPS       ┌─────────────┐
│   Browser   │ ───────────────> │   Netlify   │
│  (React)    │                  │  (Frontend) │
└─────────────┘                  └─────────────┘
      │                                │
      │ API Calls                      │
      v                                v
┌─────────────┐      HTTPS       ┌─────────────┐
│  Railway    │ <────────────────│  Supabase   │
│  (FastAPI)  │  PostgreSQL      │ (Database)  │
└─────────────┘                  └─────────────┘
```

## 📁 Project Structure

```
moviesync/
├── database/        # Database schema
├── backend/         # FastAPI + Python
├── frontend/        # React + Web Audio API
└── tools/           # Audio processing scripts
```

## 🔧 Tech Stack

**Frontend:** React + Web Audio API → Netlify  
**Backend:** FastAPI + Chromaprint → Railway  
**Database:** PostgreSQL → Supabase

## 🎯 How It Works

1. User opens app on phone while watching TV
2. Clicks "Start Listening" → records 10 seconds of audio
3. Backend matches fingerprint against ~90,000 stored fingerprints
4. Returns movie title and exact timestamp
5. Displays comments from other users at that moment
6. User can post their own comment

## 📝 License

MIT

## 🙏 Acknowledgments

- [Chromaprint](https://acoustid.org/chromaprint) by Lukáš Lalinský
- Inspired by Shazam and Genius
- Built with Claude Code
