import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import ChatHistory from './ChatHistory';
import SceneDescription from './SceneDescription';
import InputSection from './InputSection';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';
import { sendMessage, getStoryHistory, summarizeStory } from '../services/storyService';

function StoryChatPage() {
  const { storyId } = useParams();
  const navigate = useNavigate();
  
  const [chatHistory, setChatHistory] = useState([]);
  const [sceneDescription, setSceneDescription] = useState(null);
  const [loading, setLoading] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [preservedInput, setPreservedInput] = useState('');
  const [storyInfo, setStoryInfo] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);

  // Load chat history on component mount and when storyId changes
  useEffect(() => {
    if (storyId) {
      loadChatHistory();
    }
  }, [storyId]);

  const loadChatHistory = async () => {
    try {
      setInitialLoading(true);
      setError(null);
      
      const historyData = await getStoryHistory(storyId);
      setChatHistory(historyData.messages || []);
      setSceneDescription(historyData.sceneDescription || historyData.scene_description);
      
      // Extract story info if available
      if (historyData.story) {
        setStoryInfo(historyData.story);
      }
      
    } catch (err) {
      console.error('Error loading chat history:', err);
      
      if (err.response?.status === 404) {
        setError('Story not found. Please check if the story ID is correct.');
      } else {
        setError('Failed to load story. Please try again.');
      }
    } finally {
      setInitialLoading(false);
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
      // Send message to specific story
      const botResponse = await sendMessage(storyId, message);
      
      // Update scene description from bot response
      if (botResponse.scene_description) {
        setSceneDescription(botResponse.scene_description);
      }
      
      // Reload chat history to get the updated conversation
      await loadChatHistory();
      
      // Clear preserved input on success
      setPreservedInput('');
      
    } catch (err) {
      console.error('Error sending message:', err);
      
      // Preserve the input for retry
      setPreservedInput(message);
      
      // Set error message based on response
      let errorMsg = 'Failed to send message. Please try again.';
      
      if (err.response?.status === 404) {
        errorMsg = 'Story not found. Returning to dashboard...';
        // Navigate back to dashboard after a delay
        setTimeout(() => navigate('/'), 2000);
      } else if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async (messageId) => {
    setSummarizing(true);
    setError(null);

    try {
      await summarizeStory(storyId, messageId);
      
      // Reload chat history after summarization
      await loadChatHistory();
      
      // Show success message
      setSuccessMessage(`Successfully summarized conversation up to message ${messageId}! Chat history has been updated.`);
      
    } catch (err) {
      console.error('Error summarizing chat:', err);
      
      let errorMsg = 'Failed to summarize chat. Please try again.';
      
      if (err.response?.status === 404) {
        errorMsg = 'Story or message not found.';
      } else if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err.message) {
        errorMsg = err.message;
      }
      
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

  // Show loading state while initially loading
  if (initialLoading) {
    return (
      <div className="story-chat-page">
        <div className="story-chat-page__loading">
          <div className="loading-spinner"></div>
          <p>Loading story content...</p>
        </div>
      </div>
    );
  }

  // Show error state if story couldn't be loaded
  if (error && !chatHistory.length && !sceneDescription) {
    return (
      <div className="story-chat-page">
        <div className="story-chat-page__error">
          <p>{error}</p>
          <Link to="/" className="story-chat-page__return-button">Return to Dashboard</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="story-chat-page">
      <div className="container">
        <div className="main-layout">
          <div className="sidebar">
            <SceneDescription sceneDescription={sceneDescription} />
          </div>
          
          <div className="chat-section">
            <ChatHistory 
              messages={chatHistory} 
              onSummarize={handleSummarize}
              summarizing={summarizing}
            />
          </div>
        </div>

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
    </div>
  );
}

export default StoryChatPage;