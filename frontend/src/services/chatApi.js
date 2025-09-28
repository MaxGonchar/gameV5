import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`Response received:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Send a message to the chat bot
 * @param {string} message - The message to send
 * @returns {Promise<Object>} Bot response
 */
export const sendMessage = async (message) => {
  try {
    const response = await api.post('/chat/message', {
      message: message.trim()
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

/**
 * Get the complete chat history
 * @returns {Promise<Array>} Array of chat messages
 */
export const getChatHistory = async () => {
  try {
    const response = await api.get('/chat/history');
    return response.data.messages || [];
  } catch (error) {
    console.error('Error getting chat history:', error);
    throw error;
  }
};

/**
 * Summarize chat up to a specific message
 * @param {string} messageId - ID of the message to summarize up to
 * @returns {Promise<Object>} Summary response
 */
export const summarizeChat = async (messageId) => {
  try {
    const response = await api.post(`/chat/summarize/${messageId}`);
    return response.data;
  } catch (error) {
    console.error('Error summarizing chat:', error);
    throw error;
  }
};

/**
 * Check API health
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};