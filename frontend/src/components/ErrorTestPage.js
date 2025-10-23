import React, { useState } from 'react';

function ErrorTestPage() {
  const [shouldThrowError, setShouldThrowError] = useState(false);

  if (shouldThrowError) {
    throw new Error('This is a test error for the ErrorBoundary!');
  }

  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1>🧪 Error Boundary Test</h1>
      <p>Click the button below to trigger an error and test the ErrorBoundary:</p>
      <button 
        onClick={() => setShouldThrowError(true)}
        style={{
          padding: '12px 24px',
          background: '#dc2626',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          fontSize: '1rem',
          cursor: 'pointer'
        }}
      >
        🚨 Trigger Error
      </button>
    </div>
  );
}

export default ErrorTestPage;