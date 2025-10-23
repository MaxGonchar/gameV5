import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navigation() {
  const location = useLocation();
  
  // Determine current page for breadcrumb
  const getBreadcrumbInfo = () => {
    const path = location.pathname;
    
    if (path === '/') {
      return {
        title: 'Story Dashboard',
        breadcrumb: [{ label: 'Dashboard', path: '/' }]
      };
    }
    
    if (path === '/create') {
      return {
        title: 'Create New Story',
        breadcrumb: [
          { label: 'Dashboard', path: '/' },
          { label: 'Create Story', path: '/create' }
        ]
      };
    }
    
    if (path.startsWith('/story/')) {
      const storyId = path.split('/story/')[1];
      return {
        title: 'Story Adventure',
        breadcrumb: [
          { label: 'Dashboard', path: '/' },
          { label: `Story ${storyId.slice(0, 8)}...`, path: path }
        ]
      };
    }
    
    return {
      title: 'Adventure Game',
      breadcrumb: [{ label: 'Home', path: '/' }]
    };
  };

  const { title, breadcrumb } = getBreadcrumbInfo();

  return (
    <nav className="navigation">
      <div className="navigation__container">
        <div className="navigation__brand">
          <Link to="/" className="navigation__brand-link">
            <span className="navigation__logo">🎲</span>
            <span className="navigation__title">Adventure Game</span>
          </Link>
        </div>
        
        <div className="navigation__breadcrumb">
          {breadcrumb.map((crumb, index) => (
            <React.Fragment key={crumb.path}>
              {index > 0 && <span className="breadcrumb__separator">→</span>}
              {index === breadcrumb.length - 1 ? (
                <span className="breadcrumb__current">{crumb.label}</span>
              ) : (
                <Link to={crumb.path} className="breadcrumb__link">
                  {crumb.label}
                </Link>
              )}
            </React.Fragment>
          ))}
        </div>
        
        <div className="navigation__actions">
          {location.pathname !== '/' && (
            <Link to="/" className="navigation__home-button">
              🏠 Dashboard
            </Link>
          )}
          {location.pathname !== '/create' && (
            <Link to="/create" className="navigation__create-button">
              ✨ New Story
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navigation;