import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import CreateStory from './components/CreateStory';
import StoryChatPage from './components/StoryChatPage';

function App() {
  return (
    <div className="app">
      <Routes>
        {/* Dashboard - main landing page */}
        <Route path="/" element={<Dashboard />} />
        
        {/* Story Creation page */}
        <Route path="/create" element={<CreateStory />} />
        
        {/* Active Story Chat page */}
        <Route path="/story/:storyId" element={<StoryChatPage />} />
        
        {/* Fallback for unknown routes */}
        <Route path="*" element={<Dashboard />} />
      </Routes>
    </div>
  );
}

export default App;