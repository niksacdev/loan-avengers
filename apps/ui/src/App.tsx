import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import { HomePage } from './pages/home/HomePage';
import { ApplicationPage } from './pages/application/ApplicationPage';
import { ResultsPage } from './pages/results/ResultsPage';
import { NotFoundPage } from './pages/error/NotFoundPage';
import { validateConfig, logConfigInfo } from './utils/config';

/**
 * Main App component that sets up routing and global providers.
 * Implements error boundaries and accessibility features.
 */
function App() {
  // Validate configuration on app start
  if (!validateConfig()) {
    console.error('Application configuration is invalid');
  }

  // Log configuration in development
  logConfigInfo();

  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          {/* Route change announcements for screen readers */}
          <div
            id="route-announcer"
            aria-live="polite"
            aria-atomic="true"
            className="sr-only"
          />

          <Routes>
            {/* Home Page */}
            <Route path="/" element={<HomePage />} />
            
            {/* Application Flow */}
            <Route path="/application" element={<ApplicationPage />} />
            <Route path="/application/*" element={<ApplicationPage />} />
            
            {/* Results Page */}
            <Route path="/results" element={<ResultsPage />} />
            
            {/* 404 Error Page */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
