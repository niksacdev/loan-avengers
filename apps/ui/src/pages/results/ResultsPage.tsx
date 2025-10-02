import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { ExperimentalDisclaimer } from '../../components/ui/ExperimentalDisclaimer';
import { Confetti } from '../../components/ui/Confetti';

/**
 * Results page component - displays loan decision and celebration.
 * Shows the final outcome of the AI team's assessment.
 */
export function ResultsPage() {
  const navigate = useNavigate();

  // Get real decision data from session storage (set by ApplicationPage)
  const [decision, setDecision] = React.useState<any>(null);
  const [loadAttempted, setLoadAttempted] = React.useState(false);

  // Helper function to navigate to home and scroll to top
  const goToHome = () => {
    navigate('/');
    // Scroll to top after navigation
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 0);
  };

  // Load decision from sessionStorage on mount
  React.useEffect(() => {
    const storedDecision = sessionStorage.getItem('loanDecision');
    console.log('ResultsPage: Checking for stored decision');

    if (storedDecision) {
      try {
        const parsedDecision = JSON.parse(storedDecision);
        console.log('ResultsPage: Found decision in sessionStorage:', {
          status: parsedDecision.status,
          hasReasoning: !!parsedDecision.reasoning,
          hasLoanAmount: !!parsedDecision.loanAmount,
        });
        setDecision(parsedDecision);
      } catch (e) {
        console.error('ResultsPage: Failed to parse decision from sessionStorage:', e);
      }
    } else {
      console.warn('ResultsPage: No decision found in sessionStorage');
    }

    setLoadAttempted(true);
  }, []); // Only run once on mount

  // Clear sessionStorage only when navigating away from results page
  React.useEffect(() => {
    return () => {
      // Cleanup when component unmounts (user navigates away)
      sessionStorage.removeItem('loanDecision');
      console.log('ResultsPage: Cleared sessionStorage on unmount');
    };
  }, []);

  const scrollToDetails = () => {
    const detailsSection = document.getElementById('loan-details');
    if (detailsSection) {
      detailsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // If no decision data, show error
  if (!decision) {
    return (
      <Layout title="No Decision Data">
        <div className="max-w-4xl mx-auto px-4 py-16 text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-dark-text-primary mb-4">
            No loan decision found
          </h1>
          <p className="text-lg text-gray-600 dark:text-dark-text-secondary mb-8">
            Please complete the application process first.
          </p>
          <Link to="/application" className="btn-primary">
            Start Application
          </Link>
        </div>
      </Layout>
    );
  }

  // Determine status-specific content
  const status = decision.status || 'approved';
  const isApproved = status === 'approved';
  const isDenied = status === 'denied';
  const isConditional = status === 'conditional';
  const isManualReview = status === 'manual_review';

  const getHeaderContent = () => {
    if (isApproved) {
      return {
        icon: '🎉',
        title: 'Congratulations!',
        badge: { icon: '✅', text: 'Your loan has been approved!' },
        message: 'Your AI Dream Team has worked together to get you the perfect loan. Here are the exciting details!',
        bgGradient: 'from-brand-500 to-accent-600',
        showConfetti: true,
      };
    } else if (isDenied) {
      return {
        icon: '📋',
        title: 'Application Decision',
        badge: { icon: '❌', text: 'Application Not Approved' },
        message: 'After careful review, we are unable to approve your application at this time. Please review the details below.',
        bgGradient: 'from-red-500 to-red-600',
        showConfetti: false,
      };
    } else if (isConditional) {
      return {
        icon: '⚠️',
        title: 'Conditional Approval',
        badge: { icon: '📝', text: 'Additional Steps Required' },
        message: 'Great news! Your loan is conditionally approved. Please complete the requirements listed below.',
        bgGradient: 'from-warning-500 to-warning-600',
        showConfetti: false,
      };
    } else { // manual_review
      return {
        icon: '👤',
        title: 'Manual Review Required',
        badge: { icon: '🔍', text: 'Under Review' },
        message: 'Your application requires additional review by our specialist team. We will contact you shortly.',
        bgGradient: 'from-primary-500 to-primary-600',
        showConfetti: false,
      };
    }
  };

  const headerContent = getHeaderContent();

  return (
    <Layout title="Your Loan Results">
      <div className="animate-fade-in">
        {/* Confetti Animation - Only for approved */}
        {headerContent.showConfetti && <Confetti active={true} count={150} duration={8000} />}

        {/* Experimental Disclaimer */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <ExperimentalDisclaimer />
        </div>

        {/* Professional Animation - Only for approved */}
        {headerContent.showConfetti && (
          <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden" aria-hidden="true">
            {/* Vite-inspired gradient orbs */}
            <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-r from-vite-purple to-vite-blue rounded-full opacity-20 animate-pulse" style={{animationDelay: '0s', animationDuration: '4s'}}></div>
            <div className="absolute top-40 right-32 w-24 h-24 bg-gradient-to-r from-vite-orange to-vite-purple rounded-full opacity-15 animate-pulse" style={{animationDelay: '1s', animationDuration: '3s'}}></div>
            <div className="absolute bottom-32 left-40 w-20 h-20 bg-gradient-to-r from-dark-electric-blue to-dark-electric-purple rounded-full opacity-25 animate-pulse" style={{animationDelay: '2s', animationDuration: '5s'}}></div>

            {/* Floating success icons */}
            <div className="absolute top-1/4 right-1/4 text-2xl opacity-60" style={{animation: 'float 6s ease-in-out infinite', animationDelay: '0.5s'}}>
              ✨
            </div>
            <div className="absolute bottom-1/3 left-1/3 text-xl opacity-50" style={{animation: 'float 8s ease-in-out infinite', animationDelay: '1.5s'}}>
              🎉
            </div>
            <div className="absolute top-1/2 left-1/5 text-lg opacity-40" style={{animation: 'float 7s ease-in-out infinite', animationDelay: '2.5s'}}>
              ⭐
            </div>
          </div>
        )}

        {/* Decision Header */}
        <section className="relative bg-gradient-to-br from-gray-50 via-white to-brand-25/80 dark:from-dark-bg-primary dark:via-dark-bg-secondary dark:to-dark-bg-tertiary py-24 lg:py-32 overflow-hidden transition-colors duration-300">
          {/* Background decoration */}
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-100/12 via-accent-50/8 to-transparent"></div>
          <div className="absolute inset-0 bg-grid-gray-900/[0.02] bg-[size:20px_20px]"></div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            {/* Decision Icon */}
            <div className={`inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br ${headerContent.bgGradient} rounded-3xl shadow-2xl mb-8 ${isApproved ? 'animate-bounce-gentle' : ''}`}>
              <span className="text-4xl" aria-hidden="true">{headerContent.icon}</span>
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-gray-900 dark:text-dark-text-primary mb-6 transition-colors duration-300">
              {headerContent.title}
            </h1>

            <div className={`celebration-badge text-2xl lg:text-3xl mb-8 ${isDenied ? 'bg-red-50 border-red-200 text-red-800' : ''}`}>
              <span className="text-2xl mr-2">{headerContent.badge.icon}</span>
              {headerContent.badge.text}
            </div>

            <p className="text-xl lg:text-2xl text-gray-600 dark:text-dark-text-secondary max-w-3xl mx-auto leading-relaxed mb-8 transition-colors duration-300">
              {headerContent.message}
            </p>

            {/* View Details Button */}
            <button
              onClick={scrollToDetails}
              className="btn-primary text-lg px-8 py-4 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 mx-auto"
            >
              <span>View Details</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </section>

        {/* Loan Details */}
        <section id="loan-details" className="py-16 bg-white dark:bg-dark-bg-secondary transition-colors duration-300">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="card dark:bg-dark-bg-card transition-colors duration-300">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-dark-text-primary mb-6 text-center transition-colors duration-300">
                Your Loan Details
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card-elevated text-center p-8 bg-gradient-to-br from-brand-50 to-brand-100/50 border-brand-200 group hover:scale-[1.02] transition-all duration-300">
                  <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-brand-600 to-brand-700 bg-clip-text text-transparent mb-3">
                    ${decision.loanAmount.toLocaleString()}
                  </div>
                  <div className="text-gray-700 dark:text-dark-text-secondary font-medium text-lg transition-colors duration-300">Loan Amount</div>
                </div>

                <div className="card-elevated text-center p-8 bg-gradient-to-br from-success-50 to-success-100/50 border-success-200 group hover:scale-[1.02] transition-all duration-300">
                  <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-success-600 to-success-700 bg-clip-text text-transparent mb-3">
                    {decision.interestRate}%
                  </div>
                  <div className="text-gray-700 dark:text-dark-text-secondary font-medium text-lg transition-colors duration-300">Interest Rate</div>
                </div>

                <div className="card-elevated text-center p-8 bg-gradient-to-br from-warning-50 to-warning-100/50 border-warning-200 group hover:scale-[1.02] transition-all duration-300">
                  <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-warning-600 to-warning-700 bg-clip-text text-transparent mb-3">
                    ${decision.monthlyPayment.toLocaleString()}
                  </div>
                  <div className="text-gray-700 dark:text-dark-text-secondary font-medium text-lg transition-colors duration-300">Monthly Payment</div>
                </div>

                <div className="card-elevated text-center p-8 bg-gradient-to-br from-primary-50 to-primary-100/50 border-primary-200 group hover:scale-[1.02] transition-all duration-300">
                  <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 bg-clip-text text-transparent mb-3">
                    {decision.term} years
                  </div>
                  <div className="text-gray-700 dark:text-dark-text-secondary font-medium text-lg transition-colors duration-300">Loan Term</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Processing Notes - Decision Rationale */}
        <section className="py-16 bg-gray-50 dark:bg-dark-bg-tertiary transition-colors duration-300">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="card dark:bg-dark-bg-card transition-colors duration-300">
              <div className="flex items-start space-x-3 mb-4">
                <div className="bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full w-10 h-10 flex items-center justify-center text-xl flex-shrink-0 transition-colors duration-300">
                  🔍
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary transition-colors duration-300">
                  Decision Rationale
                </h2>
              </div>

              <div className="ml-13 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg transition-colors duration-300">
                <p className="text-gray-800 dark:text-dark-text-secondary leading-relaxed transition-colors duration-300">
                  {decision.reasoning || '⚠️ Decision rationale is not available. The reasoning field was not provided by the system.'}
                </p>
              </div>

              <div className="mt-4 ml-13 text-sm text-gray-600 dark:text-dark-text-muted transition-colors duration-300">
                <span className="font-medium">ℹ️ Why this matters:</span> This explanation clarifies the specific factors
                that led to your decision, ensuring transparency in our assessment process.
              </div>
            </div>
          </div>
        </section>

        {/* Next Steps */}
        <section id="next-steps" className="py-16 bg-white dark:bg-dark-bg-secondary transition-colors duration-300">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="card dark:bg-dark-bg-card transition-colors duration-300">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-6 transition-colors duration-300">
                What Happens Next?
              </h2>
              
              <div className="space-y-4">
                {decision.nextSteps.map((step: string, index: number) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="bg-primary-100 text-primary-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-medium flex-shrink-0">
                      {index + 1}
                    </div>
                    <p className="text-gray-700">{step}</p>
                  </div>
                ))}
              </div>

              {decision.conditions && decision.conditions.length > 0 && (
                <div className="mt-8 p-4 bg-yellow-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    📋 Conditions to Complete:
                  </h3>
                  <ul className="space-y-1">
                    {decision.conditions.map((condition: string, index: number) => (
                      <li key={index} className="text-gray-700 text-sm">
                        • {condition}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Actions Section */}
        <section className={`py-16 ${isApproved ? 'bg-gradient-to-br from-brand-600 via-brand-700 to-accent-700' : 'bg-gray-100 dark:bg-dark-bg-tertiary'}`}>
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            {isApproved ? (
              <>
                <h2 className="text-3xl font-bold text-white mb-4">
                  Share Your Success!
                </h2>
                <p className="text-brand-100 text-lg mb-8">
                  You've just experienced the future of loan applications.
                  Share this moment with friends and family!
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-lg mx-auto">
                  <button
                    onClick={() => {
                      alert('🎉 Shared: "Just got approved for my dream home loan with AI specialists in 15 minutes! The future is here! #LoanAvengers"');
                    }}
                    className="btn-secondary w-full sm:w-auto px-8 py-4 text-lg shadow-lg hover:shadow-xl group"
                  >
                    <span className="text-xl mr-2">📱</span>
                    <span>Share Success</span>
                    <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                    </svg>
                  </button>

                  <button
                    onClick={goToHome}
                    className="btn-success w-full sm:w-auto px-8 py-4 text-lg shadow-lg hover:shadow-xl group"
                  >
                    <span className="text-xl mr-2">🏠</span>
                    <span>Back to Home</span>
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </button>
                </div>
              </>
            ) : (
              <>
                <h2 className="text-3xl font-bold text-gray-900 dark:text-dark-text-primary mb-4 transition-colors duration-300">
                  {isDenied ? 'Explore Your Options' : 'Next Steps'}
                </h2>
                <p className="text-gray-600 dark:text-dark-text-secondary text-lg mb-8 transition-colors duration-300">
                  {isDenied
                    ? 'We understand this is disappointing. Our team is here to help you find alternative solutions.'
                    : isConditional
                      ? 'Complete the requirements and your approval will be finalized.'
                      : 'Our specialist team will review your application and contact you soon.'
                  }
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-lg mx-auto">
                  {isDenied && (
                    <Link
                      to="/application"
                      className="btn-primary w-full sm:w-auto px-8 py-4 text-lg shadow-lg hover:shadow-xl group"
                    >
                      <span className="text-xl mr-2">🔄</span>
                      <span>Try Again</span>
                      <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </Link>
                  )}

                  <button
                    onClick={goToHome}
                    className="btn-secondary w-full sm:w-auto px-8 py-4 text-lg shadow-lg hover:shadow-xl group"
                  >
                    <span className="text-xl mr-2">🏠</span>
                    <span>Back to Home</span>
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </button>
                </div>
              </>
            )}
          </div>
        </section>
      </div>
    </Layout>
  );
}