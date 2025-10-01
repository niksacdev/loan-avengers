import { Link } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { ExperimentalDisclaimer } from '../../components/ui/ExperimentalDisclaimer';
import { Confetti } from '../../components/ui/Confetti';

/**
 * Results page component - displays loan decision and celebration.
 * Shows the final outcome of the AI team's assessment.
 */
export function ResultsPage() {
  const scrollToDetails = () => {
    const detailsSection = document.getElementById('loan-details');
    if (detailsSection) {
      detailsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };
  // Mock data for demonstration - in real app, this would come from API/state
  const mockDecision = {
    status: 'approved' as const,
    loanAmount: 450000,
    interestRate: 6.2,
    monthlyPayment: 2847,
    term: 30,
    conditions: ['Income verification required', 'Home appraisal needed'],
    nextSteps: [
      'Your closing coordinator Maria will contact you within 24 hours',
      'Schedule home inspection within 2 weeks',
      'Provide final income documentation',
      'Review and sign loan documents'
    ]
  };

  return (
    <Layout title="Your Loan Results">
      <div className="animate-fade-in">
        {/* Confetti Animation */}
        <Confetti active={true} count={150} duration={8000} />

        {/* Experimental Disclaimer */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <ExperimentalDisclaimer />
        </div>
        {/* Professional Success Animation */}
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

        {/* Celebration Header */}
        <section className="relative bg-gradient-to-br from-gray-50 via-white to-brand-25/80 dark:from-dark-bg-primary dark:via-dark-bg-secondary dark:to-dark-bg-tertiary py-24 lg:py-32 overflow-hidden transition-colors duration-300">
          {/* Background decoration */}
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-100/12 via-accent-50/8 to-transparent"></div>
          <div className="absolute inset-0 bg-grid-gray-900/[0.02] bg-[size:20px_20px]"></div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            {/* Celebration Icon */}
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-brand-500 to-accent-600 rounded-3xl shadow-2xl mb-8 animate-bounce-gentle">
              <span className="text-4xl" aria-hidden="true">🎉</span>
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-gray-900 dark:text-dark-text-primary mb-6 transition-colors duration-300">
              Congratulations!
            </h1>

            <div className="celebration-badge text-2xl lg:text-3xl mb-8">
              <span className="text-2xl mr-2">✅</span>
              Your loan has been approved!
            </div>

            <p className="text-xl lg:text-2xl text-gray-600 dark:text-dark-text-secondary max-w-3xl mx-auto leading-relaxed mb-8 transition-colors duration-300">
              Your AI Dream Team has worked together to get you the perfect loan.
              Here are the exciting details!
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
                    ${mockDecision.loanAmount.toLocaleString()}
                  </div>
                  <div className="text-gray-700 dark:text-dark-text-secondary font-medium text-lg transition-colors duration-300">Loan Amount</div>
                </div>

                <div className="card-elevated text-center p-8 bg-gradient-to-br from-success-50 to-success-100/50 border-success-200 group hover:scale-[1.02] transition-all duration-300">
                  <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-success-600 to-success-700 bg-clip-text text-transparent mb-3">
                    {mockDecision.interestRate}%
                  </div>
                  <div className="text-gray-700 dark:text-dark-text-secondary font-medium text-lg transition-colors duration-300">Interest Rate</div>
                </div>

                <div className="card-elevated text-center p-8 bg-gradient-to-br from-warning-50 to-warning-100/50 border-warning-200 group hover:scale-[1.02] transition-all duration-300">
                  <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-warning-600 to-warning-700 bg-clip-text text-transparent mb-3">
                    ${mockDecision.monthlyPayment.toLocaleString()}
                  </div>
                  <div className="text-gray-700 dark:text-dark-text-secondary font-medium text-lg transition-colors duration-300">Monthly Payment</div>
                </div>

                <div className="card-elevated text-center p-8 bg-gradient-to-br from-primary-50 to-primary-100/50 border-primary-200 group hover:scale-[1.02] transition-all duration-300">
                  <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 bg-clip-text text-transparent mb-3">
                    {mockDecision.term} years
                  </div>
                  <div className="text-gray-700 dark:text-dark-text-secondary font-medium text-lg transition-colors duration-300">Loan Term</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Next Steps */}
        <section id="next-steps" className="py-16 bg-white">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                What Happens Next?
              </h2>
              
              <div className="space-y-4">
                {mockDecision.nextSteps.map((step, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="bg-primary-100 text-primary-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-medium flex-shrink-0">
                      {index + 1}
                    </div>
                    <p className="text-gray-700">{step}</p>
                  </div>
                ))}
              </div>

              {mockDecision.conditions.length > 0 && (
                <div className="mt-8 p-4 bg-yellow-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    📋 Conditions to Complete:
                  </h3>
                  <ul className="space-y-1">
                    {mockDecision.conditions.map((condition, index) => (
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

        {/* Social Sharing & Actions */}
        <section className="py-16 bg-gradient-to-br from-brand-600 via-brand-700 to-accent-700">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
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
                  // Mock social sharing
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

              <Link
                to="/"
                className="btn-success w-full sm:w-auto px-8 py-4 text-lg shadow-lg hover:shadow-xl group"
              >
                <span className="text-xl mr-2">🏠</span>
                <span>Back to Home</span>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}