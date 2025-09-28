import React, { useState, useEffect } from 'react';
import ChatHeader from './components/ChatHeader';
import ChatHistory from './components/ChatHistory';
import InputSection from './components/InputSection';
import ErrorMessage from './components/ErrorMessage';
import SuccessMessage from './components/SuccessMessage';
import * as chatApi from './services/chatApi';

function App() {
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [preservedInput, setPreservedInput] = useState('');

  // Load chat history on component mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const history = await chatApi.getChatHistory();
      setChatHistory(history);
    } catch (err) {
      console.error('Error loading chat history:', err);
      setError('Failed to load chat history. Please refresh the page.');
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) {
      setError('Message cannot be empty.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // Send message to backend
      await chatApi.sendMessage(message);
      
      // Reload chat history to get the updated conversation
      await loadChatHistory();
      
      // Clear preserved input on success
      setPreservedInput('');
      
    } catch (err) {
      console.error('Error sending message:', err);
      
      // Preserve the input for retry
      setPreservedInput(message);
      
      // Set error message
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to send message. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async (messageId) => {
    setSummarizing(true);
    setError(null);

    try {
      await chatApi.summarizeChat(messageId);
      
      // Reload chat history after summarization
      await loadChatHistory();
      
      // Show success message
      setSuccessMessage(`Successfully summarized conversation up to message ${messageId}! Chat history has been updated.`);
      
    } catch (err) {
      console.error('Error summarizing chat:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to summarize chat. Please try again.';
      setError(`Summarization failed: ${errorMsg}`);
    } finally {
      setSummarizing(false);
    }
  };

  const clearError = () => {
    setError(null);
    setPreservedInput('');
  };

  const clearSuccess = () => {
    setSuccessMessage(null);
  };

  return (
    <div className="container">
      <ChatHeader />
      
      <ChatHistory 
        messages={chatHistory} 
        onSummarize={handleSummarize}
        summarizing={summarizing}
      />
      
      {successMessage && (
        <SuccessMessage 
          message={successMessage}
          onDismiss={clearSuccess}
        />
      )}

      {error && (
        <ErrorMessage 
          message={error} 
          showTip={!!preservedInput}
          onDismiss={clearError}
        />
      )}
      
      <InputSection
        onSendMessage={handleSendMessage}
        loading={loading}
        preservedValue={preservedInput}
      />
    </div>
  );
}

export default App;