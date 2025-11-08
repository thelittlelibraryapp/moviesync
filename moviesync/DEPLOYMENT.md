# MovieSync Deployment Guide

Complete step-by-step instructions for deploying MovieSync to production.

## Prerequisites

- GitHub account
- Supabase account (free tier)
- Railway account (free tier)
- Netlify account (free tier)

## Step 1: Setup Supabase Database (10 min)

1. Go to https://supabase.com and create new project
2. Go to SQL Editor
3. Copy contents of `database/schema.sql` and execute
4. Verify 3 tables created: movies, fingerprints, comments
5. Get connection string from Project Settings > Database
6. Save for later: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`

## Step 2: Process Movie Audio Files (2-4 hours, local)

1. Install dependencies:
```bash
# Mac
brew install ffmpeg chromaprint
pip install -r tools/requirements.txt

# Ubuntu
sudo apt install ffmpeg libchromaprint-tools
pip install -r tools/requirements.txt
```

2. Create `.env` in tools/:
```bash
DATABASE_URL=your_supabase_connection_string
```

3. Add movie files to `tools/movies/` with exact names
4. Run batch processing:
```bash
cd tools
chmod +x process_all_movies.sh
./process_all_movies.sh
```

## Step 3: Deploy Backend to Railway (15 min)

1. Push code to GitHub
2. Go to https://railway.app
3. Create new project from GitHub repo
4. Set root directory: `backend`
5. Add environment variables:
   - `DATABASE_URL`: Supabase connection string
   - `CORS_ORIGINS`: `http://localhost:3000`
   - `PORT`: `8000`
6. Generate domain under Settings > Networking
7. Save Railway URL for frontend

## Step 4: Deploy Frontend to Netlify (15 min)

1. Go to https://netlify.com
2. Import from GitHub
3. Configure:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`
4. Add environment variable:
   - `REACT_APP_API_URL`: Your Railway URL
5. Deploy and copy Netlify URL

## Step 5: Update CORS (5 min)

1. Go back to Railway
2. Update `CORS_ORIGINS` variable to include Netlify URL:
   ```
   http://localhost:3000,https://your-app.netlify.app
   ```
3. Railway auto-redeploys

## Step 6: Test

1. Open Netlify URL on phone
2. Click "Start Listening"
3. Point at TV playing supported movie
4. Verify identification works
5. Post test comment

## Costs

All services have free tiers:
- Supabase: Free (500MB database)
- Railway: Free ($5 credit/month)
- Netlify: Free (100GB bandwidth/month)

**Total: $0 for MVP**

## Support

Check service logs if issues occur:
- Railway: Deployments tab
- Netlify: Deploys tab
- Supabase: Table Editor

For help, open a GitHub issue.
