import React, { useState, useEffect } from 'react';
import { getStories } from '../services/storyService';
import StoryCard from './StoryCard';

function Dashboard() {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      setLoading(true);
      setError(null);
      const storiesData = await getStories();
      setStories(storiesData.stories || []);
    } catch (err) {
      console.error('Error loading stories:', err);
      setError('Failed to load stories. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <h1>🎭 My Interactive Stories</h1>
        <div className="dashboard__loading">Loading your stories...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <h1>🎭 My Interactive Stories</h1>
        <div className="dashboard__error">
          {error}
          <button onClick={loadStories} className="dashboard__retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h1>🎭 My Interactive Stories</h1>
      
      <div className="dashboard__stories">
        {/* New Story card always appears first */}
        <StoryCard type="new-story" />
        
        {/* Existing stories */}
        {stories.map((story) => (
          <StoryCard 
            key={story.id} 
            type="existing-story" 
            story={story}
          />
        ))}
        
        {/* Show message if no existing stories */}
        {stories.length === 0 && (
          <div className="dashboard__empty-message">
            No stories yet. Create your first adventure!
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;