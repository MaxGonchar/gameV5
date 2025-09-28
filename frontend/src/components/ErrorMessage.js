import React from 'react';

const ErrorMessage = ({ message, showTip, onDismiss }) => {
  return (
    <div>
      <div className="error-message">
        ❌ {message}
        {onDismiss && (
          <button 
            onClick={onDismiss}
            style={{
              float: 'right',
              background: 'none',
              border: 'none',
              fontSize: '16px',
              cursor: 'pointer',
              padding: '0 5px'
            }}
          >
            ×
          </button>
        )}
      </div>
      
      {showTip && (
        <div className="warning-message">
          💡 <strong>Tip</strong>: Your previous input has been preserved below. You can modify it and try again!
        </div>
      )}
    </div>
  );
};

export default ErrorMessage;