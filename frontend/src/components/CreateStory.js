import React from 'react';
import { Link } from 'react-router-dom';

function CreateStory() {
  return (
    <div className="create-story">
      <h1>✨ Create New Story</h1>
      <Link to="/">← Back to Stories</Link>
      <p>Story creation form - coming soon!</p>
      <p>This will allow selecting character, location, and initial scene.</p>
    </div>
  );
}

export default CreateStory;