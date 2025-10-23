import React from 'react';
import { Link, useParams } from 'react-router-dom';

function StoryChatPage() {
  const { storyId } = useParams();

  return (
    <div className="story-chat">
      <h1>📖 Story Chat</h1>
      <Link to="/">← Back to Stories</Link>
      <p>Story ID: {storyId}</p>
      <p>Interactive chat interface - coming soon!</p>
      <p>This will show the current App.js chat functionality but for specific stories.</p>
    </div>
  );
}

export default StoryChatPage;