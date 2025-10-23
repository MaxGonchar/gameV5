import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import CreateStory from './components/CreateStory';
import StoryChatPage from './components/StoryChatPage';
import Navigation from './components/Navigation';
import ErrorBoundary from './components/ErrorBoundary';
import ErrorTestPage from './components/ErrorTestPage';

function App() {
  return (
    <ErrorBoundary>
      <div className="app">
        <Navigation />
        <main className="app__main">
          <Routes>
            {/* Dashboard - main landing page */}
            <Route path="/" element={<Dashboard />} />
            
            {/* Story Creation page */}
            <Route path="/create" element={<CreateStory />} />
            
            {/* Active Story Chat page */}
            <Route path="/story/:storyId" element={<StoryChatPage />} />
            
            {/* Error test page (development only) */}
            {process.env.NODE_ENV === 'development' && (
              <Route path="/error-test" element={<ErrorTestPage />} />
            )}
            
            {/* Fallback for unknown routes */}
            <Route path="*" element={
              <div className="not-found">
                <h1>📖 Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <Dashboard />
              </div>
            } />
          </Routes>
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;