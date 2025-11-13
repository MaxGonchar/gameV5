import api from './api';

/**
 * Get list of all user stories
 * @returns {Promise<Object>} Object containing stories array
 */
export const getStories = async () => {
  try {
    const response = await api.get('/stories');
    return response.data;
  } catch (error) {
    console.error('Error getting stories:', error);
    throw error;
  }
};

/**
 * Create a new story
 * @param {Object} storyData - Story creation data matching CreateStoryRequest
 * @returns {Promise<Object>} Created story response with story_id
 */
export const createStory = async (storyData) => {
  try {
    const response = await api.post('/stories', storyData);
    return response.data;
  } catch (error) {
    console.error('Error creating story:', error);
    throw error;
  }
};

/**
 * Send a message to the story bot
 * @param {string} storyId - The ID of the story
 * @param {string} message - The message to send
 * @returns {Promise<Object>} Bot response
 */
export const sendMessage = async (storyId, message) => {
  try {
    const response = await api.post(`/stories/${storyId}/message`, {
      message: message.trim()
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

/**
 * Get the complete story history
 * @param {string} storyId - The ID of the story
 * @returns {Promise<Object>} Object containing messages array and scene_description
 */
export const getStoryHistory = async (storyId) => {
  try {
    const response = await api.get(`/stories/${storyId}/history`);
    return {
      messages: response.data.messages || [],
      sceneDescription: response.data.scene_description || null,
      storyId: response.data.story_id || storyId
    };
  } catch (error) {
    console.error('Error getting story history:', error);
    throw error;
  }
};

/**
 * Summarize story up to a specific message
 * @param {string} storyId - The ID of the story
 * @param {string} messageId - ID of the message to summarize up to
 * @returns {Promise<Object>} Summary response
 */
export const summarizeStory = async (storyId, messageId) => {
  try {
    const response = await api.post(`/stories/${storyId}/summarize/${messageId}`);
    return response.data;
  } catch (error) {
    console.error('Error summarizing story:', error);
    throw error;
  }
};