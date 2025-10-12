import React from 'react';

const SceneDescription = ({ sceneDescription }) => {
  return (
    <div className="scene-description">
      <h2>🎭 Scene Description</h2>
      
      {sceneDescription ? (
        <div className="scene-content">
          {sceneDescription}
        </div>
      ) : (
        <div className="no-scene">
          No scene description available yet. Start a conversation to see the scene unfold!
        </div>
      )}
    </div>
  );
};

export default SceneDescription;