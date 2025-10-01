import { Link } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';

/**
 * 404 Not Found page component.
 * Displays a friendly error message when users navigate to non-existent routes.
 */
export function NotFoundPage() {
  return (
    <Layout title="Page Not Found" showNavigation={true}>
      <div className="min-h-[60vh] flex items-center justify-center px-4">
        <div className="text-center animate-fade-in">
          <div className="text-8xl mb-8" aria-hidden="true">
            🦸‍♂️❓
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Oops! Page Not Found
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl">
            It looks like one of our AI specialists misplaced this page! 
            Don't worry though, we can help you find your way back.
          </p>

          <div className="card max-w-lg mx-auto mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Where would you like to go?
            </h2>
            
            <div className="space-y-3">
              <Link
                to="/"
                className="btn-primary w-full text-center block"
              >
                🏠 Go Home
              </Link>
              
              <Link
                to="/application"
                className="btn-secondary w-full text-center block"
              >
                📝 Start Application
              </Link>
              
              <button
                onClick={() => window.history.back()}
                className="btn-secondary w-full"
              >
                ← Go Back
              </button>
            </div>
          </div>

          <div className="text-sm text-gray-500">
            <p>Error Code: 404</p>
            <p>If you think this is a mistake, please contact our support team.</p>
          </div>
        </div>
      </div>
    </Layout>
  );
}