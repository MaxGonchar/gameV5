import React from 'react';

function LocationSelector({ locations, selectedLocation, onLocationSelect, loading }) {
  return (
    <div className="selector-container">
      <label htmlFor="location-select" className="selector-label">
        Choose Location:
      </label>
      <select
        id="location-select"
        className="selector-dropdown"
        value={selectedLocation || ''}
        onChange={(e) => onLocationSelect(e.target.value)}
        disabled={loading}
      >
        <option value="">Select Location...</option>
        {locations.map((location) => (
          <option key={location.id} value={location.id}>
            {location.name}
          </option>
        ))}
      </select>
      {loading && <div className="selector-loading">Loading locations...</div>}
    </div>
  );
}

export default LocationSelector;