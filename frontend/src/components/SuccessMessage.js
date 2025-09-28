import React from 'react';

const SuccessMessage = ({ message, onDismiss }) => {
  return (
    <div className="success-message">
      ✅ {message}
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
  );
};

export default SuccessMessage;