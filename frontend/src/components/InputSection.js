import React, { useState, useEffect } from 'react';

const InputSection = ({ onSendMessage, loading, preservedValue }) => {
  const [message, setMessage] = useState('');

  // Update input when preservedValue changes (for error recovery)
  useEffect(() => {
    if (preservedValue) {
      setMessage(preservedValue);
    }
  }, [preservedValue]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!message.trim() || loading) {
      return;
    }

    onSendMessage(message.trim());
    
    // Only clear the input if there's no preserved value (successful submission)
    if (!preservedValue) {
      setMessage('');
    }
  };

  const handleChange = (e) => {
    setMessage(e.target.value);
  };

  return (
    <div className="input-section">
      <h2>📝 Send a Message</h2>
      
      <form onSubmit={handleSubmit} className="input-form">
        <textarea
          className="input-textarea"
          value={message}
          onChange={handleChange}
          placeholder="Type your message here..."
          disabled={loading}
          rows={4}
        />
        
        <button
          type="submit"
          className="submit-button"
          disabled={loading || !message.trim()}
        >
          {loading ? (
            <span className="loading">Sending message...</span>
          ) : (
            'Send Message'
          )}
        </button>
      </form>
    </div>
  );
};

export default InputSection;