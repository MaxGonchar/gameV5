import React from 'react';
import { useNavigate } from 'react-router-dom';

function StoryCard({ type, story, onClick }) {
  const navigate = useNavigate();

  if (type === 'new-story') {
    return (
      <div 
        className="story-card story-card--new-story" 
        onClick={() => navigate('/create')}
        role="button"
        tabIndex={0}
        onKeyPress={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            navigate('/create');
          }
        }}
      >
        <div className="story-card__icon">✨</div>
        <div className="story-card__title">New Story</div>
        <div className="story-card__description">
          Create your next adventure...
        </div>
      </div>
    );
  }

  // Existing story card
  return (
    <div className="story-card story-card--existing">
      <div className="story-card__icon">📖</div>
      <div className="story-card__title">{story.title}</div>
      <button 
        className="story-card__button"
        onClick={() => navigate(`/story/${story.id}`)}
      >
        Continue ▶
      </button>
    </div>
  );
}

export default StoryCard;