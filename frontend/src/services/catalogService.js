import api from './api';

/**
 * Get list of all available characters
 * @returns {Promise<Object>} Object containing characters array
 */
export const getCharacters = async () => {
  try {
    const response = await api.get('/characters');
    return response.data;
  } catch (error) {
    console.error('Error getting characters:', error);
    throw error;
  }
};

/**
 * Get list of all available locations
 * @returns {Promise<Object>} Object containing locations array
 */
export const getLocations = async () => {
  try {
    const response = await api.get('/locations');
    return response.data;
  } catch (error) {
    console.error('Error getting locations:', error);
    throw error;
  }
};