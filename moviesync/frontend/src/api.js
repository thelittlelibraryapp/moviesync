/**
 * API client for MovieSync backend
 * Handles all communication with FastAPI backend
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Match audio fingerprint to identify movie and timestamp
 * @param {string} audioBase64 - Base64 encoded WAV audio
 * @returns {Promise} Match result
 */
export const matchAudio = async (audioBase64) => {
  try {
    const response = await api.post('/api/match', {
      audio: audioBase64,
    });
    return response.data;
  } catch (error) {
    console.error('Error matching audio:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Network error. Please check your connection.',
    };
  }
};

/**
 * Get comments near a timestamp
 * @param {number} movieId - Movie ID
 * @param {number} timestamp - Timestamp in seconds
 * @param {number} window - Time window in seconds (default 30)
 * @returns {Promise} Comments data
 */
export const getComments = async (movieId, timestamp, window = 30) => {
  try {
    const response = await api.get('/api/comments', {
      params: {
        movie_id: movieId,
        timestamp: timestamp,
        window: window,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching comments:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to load comments.',
    };
  }
};

/**
 * Post a new comment
 * @param {number} movieId - Movie ID
 * @param {number} timestamp - Timestamp in seconds
 * @param {string} username - Username
 * @param {string} text - Comment text
 * @returns {Promise} Post result
 */
export const postComment = async (movieId, timestamp, username, text) => {
  try {
    const response = await api.post('/api/comment', {
      movie_id: movieId,
      timestamp_seconds: timestamp,
      username: username,
      text: text,
    });
    return response.data;
  } catch (error) {
    console.error('Error posting comment:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to post comment.',
    };
  }
};

/**
 * Get all available movies
 * @returns {Promise} Movies list
 */
export const getMovies = async () => {
  try {
    const response = await api.get('/api/movies');
    return response.data;
  } catch (error) {
    console.error('Error fetching movies:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to load movies.',
    };
  }
};

export default api;
