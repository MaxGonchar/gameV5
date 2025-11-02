import React from 'react';

function CharacterSelector({ characters, selectedCharacter, onCharacterSelect, loading }) {
  return (
    <div className="selector-container">
      <label htmlFor="character-select" className="selector-label">
        Choose Character:
      </label>
      <select
        id="character-select"
        className="selector-dropdown"
        value={selectedCharacter || ''}
        onChange={(e) => onCharacterSelect(e.target.value)}
        disabled={loading}
      >
        <option value="">Select Character...</option>
        {characters.map((character) => (
          <option key={character.id} value={character.id}>
            {character.name}
          </option>
        ))}
      </select>
      {loading && <div className="selector-loading">Loading characters...</div>}
    </div>
  );
}

export default CharacterSelector;