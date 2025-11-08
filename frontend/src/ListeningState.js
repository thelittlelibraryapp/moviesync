/**
 * ListeningState Component
 * UI for the listening/recording state
 */

import React, { useState, useEffect } from 'react';
import AudioRecorder from './AudioRecorder';
import { matchAudio } from './api';

const ListeningState = ({ onMatchFound }) => {
  const [status, setStatus] = useState('idle'); // idle, recording, processing
  const [secondsRemaining, setSecondsRemaining] = useState(10);
  const [error, setError] = useState(null);
  const [recorder] = useState(() => new AudioRecorder());

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (recorder) {
        recorder.cleanup();
      }
    };
  }, [recorder]);

  const startListening = async () => {
    try {
      setError(null);
      setStatus('recording');
      setSecondsRemaining(10);

      // Countdown timer
      const countdownInterval = setInterval(() => {
        setSecondsRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(countdownInterval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      // Start recording (10 seconds)
      const result = await recorder.startRecording(10);

      if (!result.success) {
        throw new Error(result.error || 'Recording failed');
      }

      // Switch to processing state
      setStatus('processing');

      // Send to backend for matching
      const matchResult = await matchAudio(result.audio);

      if (matchResult.success) {
        // Match found!
        onMatchFound({
          movieId: matchResult.movie_id,
          title: matchResult.title,
          year: matchResult.year,
          timestamp: matchResult.timestamp_seconds,
          timestampFormatted: matchResult.timestamp_formatted,
          confidence: matchResult.confidence,
        });
      } else {
        // No match found
        setError(matchResult.error || 'No matching movie found');
        setStatus('idle');
      }

    } catch (err) {
      console.error('Error during listening:', err);
      setError(err.message || 'An error occurred. Please try again.');
      setStatus('idle');
    }
  };

  return (
    <div className="listening-state">
      <div className="header">
        <h1>🎬 MovieSync</h1>
        <p className="tagline">Know what everyone's thinking, at every moment</p>
      </div>

      {status === 'idle' && (
        <>
          <button className="btn-primary" onClick={startListening}>
            Start Listening
          </button>
          <p className="instruction">Point your phone at your TV</p>
        </>
      )}

      {status === 'recording' && (
        <div className="recording-container">
          <div className="recording-box">
            <div className="recording-icon">🎙️</div>
            <h2>Recording</h2>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${((10 - secondsRemaining) / 10) * 100}%` }}
              />
            </div>
            <p className="timer">{secondsRemaining} seconds remaining</p>
          </div>
          <div className="waveform">
            <div className="wave" />
            <div className="wave" />
            <div className="wave" />
            <div className="wave" />
            <div className="wave" />
          </div>
        </div>
      )}

      {status === 'processing' && (
        <div className="processing-container">
          <div className="spinner" />
          <p>Identifying movie...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button className="btn-secondary" onClick={() => setError(null)}>
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default ListeningState;
