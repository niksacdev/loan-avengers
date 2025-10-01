import { Component, type ErrorInfo, type ReactNode } from 'react';
import type { ErrorInfo as AppErrorInfo } from '../../types';

interface Props {
  children: ReactNode;
  fallback?: (error: AppErrorInfo) => ReactNode;
}

interface State {
  hasError: boolean;
  error: AppErrorInfo | null;
}

/**
 * Error Boundary component that catches JavaScript errors in the component tree
 * and displays a fallback UI instead of crashing the entire application.
 * 
 * Implements accessibility best practices with proper ARIA labels and error announcements.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    // Convert the error to our internal ErrorInfo format
    const appError: AppErrorInfo = {
      code: 'REACT_ERROR',
      message: error.message || 'An unexpected error occurred',
      details: error.stack,
      recoverable: true,
      retryAction: () => window.location.reload(),
    };

    return { hasError: true, error: appError };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (import.meta.env.DEV) {
      console.error('Error Boundary caught an error:', error, errorInfo);
    }

    // In production, you might want to log to an error reporting service
    // Example: logErrorToService(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    if (this.state.error?.retryAction) {
      this.state.error.retryAction();
    }
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // If custom fallback is provided, use it
      if (this.props.fallback) {
        return this.props.fallback(this.state.error);
      }

      // Default error UI
      return (
        <div 
          className="min-h-screen flex items-center justify-center bg-gray-50 px-4"
          role="alert"
          aria-live="assertive"
        >
          <div className="max-w-md w-full card text-center animate-fade-in">
            <div className="text-red-500 text-6xl mb-4" aria-hidden="true">
              🚨
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Oops! Something went wrong
            </h1>
            
            <p className="text-gray-600 mb-6">
              {this.state.error.message}
            </p>

            {this.state.error.recoverable && (
              <div className="space-y-3">
                <button
                  onClick={this.handleRetry}
                  className="btn-primary w-full"
                  aria-label="Try again to reload the application"
                >
                  Try Again
                </button>
                
                <button
                  onClick={() => window.location.href = '/'}
                  className="btn-secondary w-full"
                  aria-label="Go back to home page"
                >
                  Go Home
                </button>
              </div>
            )}

            {import.meta.env.DEV && this.state.error.details && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                  Error Details (Development)
                </summary>
                <pre className="mt-2 text-xs text-gray-600 bg-gray-100 p-3 rounded overflow-auto max-h-40">
                  {this.state.error.details}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}