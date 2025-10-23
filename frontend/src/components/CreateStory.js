import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getCharacters, getLocations } from '../services/catalogService';
import { createStory } from '../services/storyService';
import CharacterSelector from './CharacterSelector';
import LocationSelector from './LocationSelector';

function CreateStory() {
  const navigate = useNavigate();
  
  // Form state
  const [selectedCharacter, setSelectedCharacter] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const [sceneDescription, setSceneDescription] = useState('');
  
  // Data state
  const [characters, setCharacters] = useState([]);
  const [locations, setLocations] = useState([]);
  
  // UI state
  const [loading, setLoading] = useState({ characters: true, locations: true });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCatalogData();
  }, []);

  const loadCatalogData = async () => {
    try {
      setError(null);
      
      // Load characters and locations in parallel
      const [charactersResponse, locationsResponse] = await Promise.all([
        getCharacters(),
        getLocations()
      ]);
      
      setCharacters(charactersResponse.characters || []);
      setLocations(locationsResponse.locations || []);
      
    } catch (err) {
      console.error('Error loading catalog data:', err);
      setError('Failed to load characters and locations. Please try again.');
    } finally {
      setLoading({ characters: false, locations: false });
    }
  };

  const handleCreateStory = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!selectedCharacter || !selectedLocation || !sceneDescription.trim()) {
      setError('Please fill in all fields before creating the story.');
      return;
    }

    setCreating(true);
    setError(null);

    try {
      const response = await createStory(
        selectedCharacter,
        selectedLocation,
        sceneDescription.trim()
      );
      
      // Navigate to the new story
      navigate(`/story/${response.story_id}`);
      
    } catch (err) {
      console.error('Error creating story:', err);
      setError(
        err.response?.data?.detail || 
        err.message || 
        'Failed to create story. Please try again.'
      );
    } finally {
      setCreating(false);
    }
  };

  const isFormValid = selectedCharacter && selectedLocation && sceneDescription.trim();

  return (
    <div className="create-story">
      <form onSubmit={handleCreateStory} className="create-story__form">
        {/* Side-by-side dropdowns */}
        <div className="create-story__selectors">
          <CharacterSelector
            characters={characters}
            selectedCharacter={selectedCharacter}
            onCharacterSelect={setSelectedCharacter}
            loading={loading.characters}
          />
          
          <LocationSelector
            locations={locations}
            selectedLocation={selectedLocation}
            onLocationSelect={setSelectedLocation}
            loading={loading.locations}
          />
        </div>

        {/* Scene description */}
        <div className="create-story__scene-section">
          <label htmlFor="scene-description" className="create-story__scene-label">
            Initial Scene Description:
          </label>
          <textarea
            id="scene-description"
            className="create-story__scene-textarea"
            value={sceneDescription}
            onChange={(e) => setSceneDescription(e.target.value)}
            placeholder="Describe the opening scene of your story..."
            rows={6}
            disabled={creating}
            required
          />
          <div className="create-story__char-count">
            {sceneDescription.length} characters
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="create-story__error">
            {error}
          </div>
        )}

        {/* Action buttons */}
        <div className="create-story__actions">
          <Link to="/" className="create-story__cancel-button">
            Cancel
          </Link>
          <button
            type="submit"
            className="create-story__create-button"
            disabled={!isFormValid || creating}
          >
            {creating ? 'Creating Story...' : 'Create Story & Begin Adventure'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateStory;