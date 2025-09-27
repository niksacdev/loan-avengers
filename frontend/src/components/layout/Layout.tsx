import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { config } from '../../utils/config';

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
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Skip to main content link for accessibility */}
      <a
        href={`#${config.accessibility.skipLinkTarget}`}
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 btn-primary"
      >
        Skip to main content
      </a>

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
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
                  <h1 className="text-xl font-bold text-gray-900">
                    {config.app.name}
                  </h1>
                  {title && (
                    <p className="text-sm text-gray-600 hidden sm:block">
                      {title}
                    </p>
                  )}
                </div>
              </Link>
            </div>

            {/* Navigation */}
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
              © 2024 {config.app.name}. Making loan dreams come true.
            </div>
            
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <button
                onClick={() => window.location.href = 'mailto:support@loanavengers.com'}
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