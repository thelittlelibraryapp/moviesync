/**
 * MovieSync Main App Component
 * Manages state between listening and comment feed views
 */

import React, { useState } from 'react';
import ListeningState from './ListeningState';
import CommentFeed from './CommentFeed';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('listening'); // 'listening' or 'feed'
  const [matchData, setMatchData] = useState(null);

  const handleMatchFound = (match) => {
    setMatchData(match);
    setCurrentView('feed');
  };

  const handleListenAgain = () => {
    setMatchData(null);
    setCurrentView('listening');
  };

  return (
    <div className="app">
      <div className="container">
        {currentView === 'listening' ? (
          <ListeningState onMatchFound={handleMatchFound} />
        ) : (
          <CommentFeed match={matchData} onListenAgain={handleListenAgain} />
        )}
      </div>
    </div>
  );
}

export default App;
