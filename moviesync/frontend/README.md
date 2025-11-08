# MovieSync Frontend

React web application for MovieSync audio fingerprinting and timestamped comments.

## Features

- Web Audio API microphone recording
- Audio fingerprint matching
- Real-time comment feed
- Mobile-first responsive design
- Works on any modern browser

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your backend API URL
```

3. Start development server:
```bash
npm start
```

4. Open http://localhost:3000

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

## Deployment to Netlify

1. Push code to GitHub
2. Create new site in Netlify
3. Connect GitHub repository
4. Configure build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`
5. Add environment variable:
   - `REACT_APP_API_URL`: Your backend API URL
6. Deploy!

## Environment Variables

- `REACT_APP_API_URL`: Backend API URL (e.g., https://your-api.railway.app)

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (HTTPS required for microphone)
- Mobile Safari (iOS 14.3+): Full support
- Android Chrome: Full support

## Components

- `App.js`: Main component with state management
- `ListeningState.js`: Recording UI and audio capture
- `CommentFeed.js`: Comment display and posting
- `AudioRecorder.js`: Web Audio API recording logic
- `api.js`: Backend API client

## License

MIT
