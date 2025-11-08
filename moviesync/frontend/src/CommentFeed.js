/**
 * CommentFeed Component
 * Displays comments and allows posting new comments
 */

import React, { useState, useEffect } from 'react';
import { getComments, postComment } from './api';

const CommentFeed = ({ match, onListenAgain }) => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState('');
  const [commentText, setCommentText] = useState('');
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState(null);
  const [postSuccess, setPostSuccess] = useState(false);

  useEffect(() => {
    loadComments();
    // Refresh comments every 10 seconds
    const interval = setInterval(loadComments, 10000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [match.movieId, match.timestamp]);

  const loadComments = async () => {
    try {
      const result = await getComments(match.movieId, match.timestamp, 30);
      if (result.success) {
        setComments(result.comments);
      } else {
        console.error('Failed to load comments:', result.error);
      }
    } catch (err) {
      console.error('Error loading comments:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePostComment = async (e) => {
    e.preventDefault();
    setError(null);
    setPostSuccess(false);

    // Validation
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }
    if (!commentText.trim()) {
      setError('Please enter a comment');
      return;
    }
    if (username.length > 50) {
      setError('Username must be 50 characters or less');
      return;
    }
    if (commentText.length > 280) {
      setError('Comment must be 280 characters or less');
      return;
    }

    setPosting(true);

    try {
      const result = await postComment(
        match.movieId,
        match.timestamp,
        username.trim(),
        commentText.trim()
      );

      if (result.success) {
        setPostSuccess(true);
        setCommentText('');
        // Reload comments to show the new one
        await loadComments();
        setTimeout(() => setPostSuccess(false), 3000);
      } else {
        setError(result.error || 'Failed to post comment');
      }
    } catch (err) {
      setError('An error occurred while posting your comment');
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className="comment-feed">
      <div className="header">
        <div className="header-content">
          <h1>🎬 MovieSync</h1>
          <button className="btn-listen-again" onClick={onListenAgain}>
            Listen Again
          </button>
        </div>
      </div>

      <div className="movie-info">
        <h2>{match.title} ({match.year})</h2>
        <p className="timestamp">📍 You're at {match.timestampFormatted}</p>
        {match.confidence && (
          <p className="confidence">Match confidence: {(match.confidence * 100).toFixed(0)}%</p>
        )}
      </div>

      <div className="comments-section">
        <h3>
          {loading ? 'Loading comments...' : `Showing ${comments.length} comment${comments.length !== 1 ? 's' : ''} nearby`}
        </h3>

        <div className="comments-list">
          {comments.length === 0 && !loading && (
            <div className="no-comments">
              <p>No comments yet at this timestamp.</p>
              <p>Be the first to share your thoughts!</p>
            </div>
          )}

          {comments.map((comment) => (
            <div key={comment.id} className="comment-card">
              <div className="comment-header">
                <span className="comment-username">{comment.username}</span>
                <span className="comment-timestamp">{comment.timestamp_formatted}</span>
              </div>
              <p className="comment-text">{comment.text}</p>
              <span className="comment-time">{comment.time_ago}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="post-comment-section">
        <h3>Post a comment:</h3>
        <form onSubmit={handlePostComment}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            maxLength={50}
            disabled={posting}
            className="input-username"
          />
          <textarea
            placeholder="Share your thoughts..."
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            maxLength={280}
            rows={3}
            disabled={posting}
            className="input-comment"
          />
          <div className="char-count">
            {commentText.length}/280 characters
          </div>
          {error && <div className="error-message">{error}</div>}
          {postSuccess && <div className="success-message">Comment posted successfully!</div>}
          <button
            type="submit"
            className="btn-primary"
            disabled={posting || !username.trim() || !commentText.trim()}
          >
            {posting ? 'Posting...' : 'Post Comment'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CommentFeed;
