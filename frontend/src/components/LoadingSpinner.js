import React from 'react';

function LoadingSpinner({ size = 'medium', message = 'Loading...', className = '' }) {
  const sizeClass = `loading-spinner--${size}`;
  
  return (
    <div className={`loading-spinner ${sizeClass} ${className}`}>
      <div className="loading-spinner__circle"></div>
      {message && (
        <p className="loading-spinner__message">{message}</p>
      )}
    </div>
  );
}

export default LoadingSpinner;