import React from 'react';
import { Link } from 'react-router-dom';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error);
    console.error('Error info:', errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  handleRetry = () => {
    // Reset error state to retry rendering
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null 
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-boundary__container">
            <div className="error-boundary__icon">🚨</div>
            <h1 className="error-boundary__title">Oops! Something went wrong</h1>
            <p className="error-boundary__message">
              We encountered an unexpected error. Don't worry, your data is safe.
            </p>
            
            <div className="error-boundary__actions">
              <button 
                onClick={this.handleRetry}
                className="error-boundary__retry-button"
              >
                🔄 Try Again
              </button>
              <Link 
                to="/" 
                className="error-boundary__home-button"
                onClick={() => this.handleRetry()}
              >
                🏠 Go to Dashboard
              </Link>
            </div>
            
            {process.env.NODE_ENV === 'development' && (
              <details className="error-boundary__details">
                <summary className="error-boundary__details-summary">
                  🔍 Developer Details
                </summary>
                <div className="error-boundary__error-info">
                  <h3>Error:</h3>
                  <pre className="error-boundary__error-text">
                    {this.state.error && this.state.error.toString()}
                  </pre>
                  
                  <h3>Component Stack:</h3>
                  <pre className="error-boundary__stack-trace">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;