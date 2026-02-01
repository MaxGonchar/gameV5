import React from 'react';

function CharacterSelector({ characters, selectedCharacter, onCharacterSelect, loading }) {
  return (
    <div className="character-selector">
      <label htmlFor="character-select" className="character-selector__label">
        Choose Character:
      </label>
      <select
        id="character-select"
        className="character-selector__select"
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
      {loading && <div className="character-selector__loading">Loading characters...</div>}
    </div>
  );
}

export default CharacterSelector;