import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { config } from '../../utils/config';
import { ThemeToggle } from '../ui/ThemeToggle';

interface LayoutProps {
  children: ReactNode;
  title?: string;
  showNavigation?: boolean;
}

/**
 * Main layout component that provides consistent structure across all pages.
 * Implements mobile-first responsive design and accessibility best practices.
 */
export function Layout({ 
  children, 
  title, 
  showNavigation = true 
}: LayoutProps) {
  const location = useLocation();

  const navigationItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/application', label: 'Apply', icon: '📝' },
    { path: '/results', label: 'Results', icon: '🎉' },
  ];

  const isActivePath = (path: string) => {
    return location.pathname === path || 
           (path !== '/' && location.pathname.startsWith(path));
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg-primary flex flex-col transition-colors duration-300">
      {/* Skip to main content link for accessibility */}
      <a
        href={`#${config.accessibility.skipLinkTarget}`}
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 btn-primary"
      >
        Skip to main content
      </a>

      {/* Header */}
      <header className="bg-white dark:bg-dark-bg-secondary shadow-sm border-b border-gray-200 dark:border-dark-bg-tertiary transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <Link 
                to="/" 
                className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
                aria-label="Go to home page"
              >
                <div className="text-2xl" aria-hidden="true">🦸‍♂️</div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-dark-text-primary transition-colors duration-300">
                    {config.app.name}
                  </h1>
                  {title && (
                    <p className="text-sm text-gray-600 dark:text-dark-text-secondary hidden sm:block transition-colors duration-300">
                      {title}
                    </p>
                  )}
                </div>
              </Link>
            </div>

            {/* Navigation & GitHub Link */}
            <div className="flex items-center space-x-4">
              {/* Theme Toggle */}
              <ThemeToggle />
              {showNavigation && (
                <nav role="navigation" aria-label="Main navigation">
                  <ul className="flex space-x-1 sm:space-x-4">
                    {navigationItems.map((item) => (
                      <li key={item.path}>
                        <Link
                          to={item.path}
                          className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                            isActivePath(item.path)
                              ? 'bg-primary-100 text-primary-700'
                              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                          }`}
                          aria-current={isActivePath(item.path) ? 'page' : undefined}
                        >
                          <span aria-hidden="true">{item.icon}</span>
                          <span className="hidden sm:inline">{item.label}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </nav>
              )}

              {/* GitHub Repository Link */}
              <a
                href="https://github.com/niksacdev/loan-defenders"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 dark:text-dark-text-secondary hover:text-gray-900 dark:hover:text-dark-text-primary hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary transition-colors duration-300"
                aria-label="View source code on GitHub"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
                <span className="hidden sm:inline">GitHub</span>
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main 
        id={config.accessibility.skipLinkTarget}
        className="flex-1 focus:outline-none"
        tabIndex={-1}
      >
        {/* Page Title for Screen Readers */}
        {title && (
          <h1 className="sr-only">
            {title} - {config.app.name}
          </h1>
        )}
        
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <div className="text-sm text-gray-600 mb-4 sm:mb-0">
              <div>© 2024 {config.app.name}. Making loan dreams come true.</div>
              <div className="text-xs text-gray-500 mt-1">
                🧪 Experimental app powered by{' '}
                <span className="font-medium text-brand-600">Microsoft Agent Framework</span>
                {' '}& <span className="font-medium text-accent-600">Microsoft AI Foundry</span>
              </div>
            </div>

            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <button
                onClick={() => window.location.href = 'mailto:support@loandefenders.com'}
                className="hover:text-gray-900 transition-colors"
              >
                Support
              </button>
              <button
                onClick={() => console.info('Privacy policy would open here')}
                className="hover:text-gray-900 transition-colors"
              >
                Privacy
              </button>
              <div className="text-xs text-gray-500">
                v{config.app.version}
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}