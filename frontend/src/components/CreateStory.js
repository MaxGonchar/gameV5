import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getCharacters } from '../services/catalogService';
import { createStory } from '../services/storyService';
import CharacterSelector from './CharacterSelector';

function CreateStory() {
  const navigate = useNavigate();
  
  // Form state
  const [selectedCharacter, setSelectedCharacter] = useState('');
  const [storyTitle, setStoryTitle] = useState('');
  const [companionName, setCompanionName] = useState('');
  const [companionDescription, setCompanionDescription] = useState('');
  const [companionContext, setCompanionContext] = useState('');
  const [meetingLocationDescription, setMeetingLocationDescription] = useState('');
  const [meetingDescription, setMeetingDescription] = useState('');
  
  // Data state
  const [characters, setCharacters] = useState([]);
  
  // UI state
  const [loading, setLoading] = useState({ characters: true });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCatalogData();
  }, []);

  const loadCatalogData = async () => {
    try {
      setError(null);
      
      const charactersResponse = await getCharacters();
      setCharacters(charactersResponse.characters || []);
      
    } catch (err) {
      console.error('Error loading catalog data:', err);
      setError('Failed to load characters. Please try again.');
    } finally {
      setLoading({ characters: false });
    }
  };

  const handleCreateStory = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!selectedCharacter || !storyTitle.trim() || !companionName.trim() || 
        !companionDescription.trim() || !companionContext.trim() || 
        !meetingLocationDescription.trim() || !meetingDescription.trim()) {
      setError('Please fill in all fields before creating the story.');
      return;
    }

    setCreating(true);
    setError(null);

    try {
      const response = await createStory({
        character_id: selectedCharacter,
        story_title: storyTitle.trim(),
        companion_name: companionName.trim(),
        companion_description: companionDescription.trim(),
        companion_context: companionContext.trim(),
        meeting_location_description: meetingLocationDescription.trim(),
        meeting_description: meetingDescription.trim()
      });
      
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

  const isFormValid = selectedCharacter && storyTitle.trim() && companionName.trim() && 
                      companionDescription.trim() && companionContext.trim() && 
                      meetingLocationDescription.trim() && meetingDescription.trim();

  return (
    <div className="create-story">
      <form onSubmit={handleCreateStory} className="create-story__form">
        {/* Character selector */}
        <div className="create-story__selectors">
          <CharacterSelector
            characters={characters}
            selectedCharacter={selectedCharacter}
            onCharacterSelect={setSelectedCharacter}
            loading={loading.characters}
          />
        </div>

        {/* Story title */}
        <div className="create-story__scene-section">
          <label htmlFor="story-title" className="create-story__scene-label">
            Story Title:
          </label>
          <input
            id="story-title"
            type="text"
            className="create-story__scene-textarea"
            style={{minHeight: 'auto', height: '48px', resize: 'none'}}
            value={storyTitle}
            onChange={(e) => setStoryTitle(e.target.value)}
            placeholder="Enter the title of your story..."
            disabled={creating}
            required
          />
        </div>

        {/* Companion name */}
        <div className="create-story__scene-section">
          <label htmlFor="companion-name" className="create-story__scene-label">
            Your Character Name:
          </label>
          <input
            id="companion-name"
            type="text"
            className="create-story__scene-textarea"
            style={{minHeight: 'auto', height: '48px', resize: 'none'}}
            value={companionName}
            onChange={(e) => setCompanionName(e.target.value)}
            placeholder="What should you be called in the story?"
            disabled={creating}
            required
          />
        </div>

        {/* Companion description */}
        <div className="create-story__scene-section">
          <label htmlFor="companion-description" className="create-story__scene-label">
            Your Character Description:
          </label>
          <textarea
            id="companion-description"
            className="create-story__scene-textarea"
            value={companionDescription}
            onChange={(e) => setCompanionDescription(e.target.value)}
            placeholder="Describe your character's appearance, personality, background..."
            rows={4}
            disabled={creating}
            required
          />
          <div className="create-story__char-count">
            {companionDescription.length} characters
          </div>
        </div>

        {/* Companion context */}
        <div className="create-story__scene-section">
          <label htmlFor="companion-context" className="create-story__scene-label">
            Background Context:
          </label>
          <textarea
            id="companion-context"
            className="create-story__scene-textarea"
            value={companionContext}
            onChange={(e) => setCompanionContext(e.target.value)}
            placeholder="Provide your background context about the world, setting, or situation..."
            rows={4}
            disabled={creating}
            required
          />
          <div className="create-story__char-count">
            {companionContext.length} characters
          </div>
        </div>

        {/* Meeting location description */}
        <div className="create-story__scene-section">
          <label htmlFor="meeting-location" className="create-story__scene-label">
            Meeting Location:
          </label>
          <textarea
            id="meeting-location"
            className="create-story__scene-textarea"
            value={meetingLocationDescription}
            onChange={(e) => setMeetingLocationDescription(e.target.value)}
            placeholder="Describe where you and the character will meet..."
            rows={3}
            disabled={creating}
            required
          />
          <div className="create-story__char-count">
            {meetingLocationDescription.length} characters
          </div>
        </div>

        {/* Meeting description */}
        <div className="create-story__scene-section">
          <label htmlFor="meeting-description" className="create-story__scene-label">
            How You Meet:
          </label>
          <textarea
            id="meeting-description"
            className="create-story__scene-textarea"
            value={meetingDescription}
            onChange={(e) => setMeetingDescription(e.target.value)}
            placeholder="Describe how the meeting happens and the initial scenario..."
            rows={4}
            disabled={creating}
            required
          />
          <div className="create-story__char-count">
            {meetingDescription.length} characters
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