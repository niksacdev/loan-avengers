import { Link } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';

/**
 * Results page component - displays loan decision and celebration.
 * Shows the final outcome of the AI team's assessment.
 */
export function ResultsPage() {
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

  const agentMessages = [
    {
      name: 'Sarah',
      role: 'Credit Specialist',
      emoji: '💼',
      message: 'Your credit profile is excellent! You qualify for our best rates.',
      score: 'A+'
    },
    {
      name: 'Marcus',
      role: 'Income Specialist',
      emoji: '📊',
      message: 'Your income is well-documented and stable. Great job!',
      score: 'A'
    },
    {
      name: 'Alex',
      role: 'Risk Advisor',
      emoji: '🛡️',
      message: 'Low risk profile with strong financial fundamentals.',
      score: 'A+'
    },
    {
      name: 'Riley',
      role: 'Loan Orchestrator',
      emoji: '🎭',
      message: 'Congratulations! The team unanimously approves your loan!',
      score: 'APPROVED'
    }
  ];

  return (
    <Layout title="Your Loan Results">
      <div className="animate-fade-in">
        {/* Celebration Header */}
        <section className="bg-gradient-to-br from-green-50 to-primary-50 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            {/* Confetti Animation */}
            <div className="text-8xl mb-6 animate-bounce-gentle" aria-hidden="true">
              🎉
            </div>
            
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
              Congratulations!
            </h1>
            
            <p className="text-2xl text-green-600 font-semibold mb-6">
              Your loan has been approved!
            </p>
            
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Your AI Dream Team has worked together to get you the perfect loan. 
              Here are the exciting details!
            </p>
          </div>
        </section>

        {/* Loan Details */}
        <section className="py-16 bg-white">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="card">
              <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
                Your Loan Details
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="text-center p-6 bg-primary-50 rounded-lg">
                  <div className="text-3xl font-bold text-primary-600 mb-2">
                    ${mockDecision.loanAmount.toLocaleString()}
                  </div>
                  <div className="text-gray-600">Loan Amount</div>
                </div>
                
                <div className="text-center p-6 bg-secondary-50 rounded-lg">
                  <div className="text-3xl font-bold text-secondary-600 mb-2">
                    {mockDecision.interestRate}%
                  </div>
                  <div className="text-gray-600">Interest Rate</div>
                </div>
                
                <div className="text-center p-6 bg-accent-50 rounded-lg">
                  <div className="text-3xl font-bold text-accent-600 mb-2">
                    ${mockDecision.monthlyPayment.toLocaleString()}
                  </div>
                  <div className="text-gray-600">Monthly Payment</div>
                </div>
                
                <div className="text-center p-6 bg-gray-50 rounded-lg">
                  <div className="text-3xl font-bold text-gray-600 mb-2">
                    {mockDecision.term} years
                  </div>
                  <div className="text-gray-600">Loan Term</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* AI Team Assessments */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                What Your AI Team Says
              </h2>
              <p className="text-lg text-gray-600">
                Each specialist has reviewed your application and given you their assessment.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {agentMessages.map((agent, index) => (
                <div
                  key={agent.name}
                  className="card text-center hover:shadow-lg transition-shadow animate-slide-up"
                  style={{ animationDelay: `${index * 150}ms` }}
                >
                  <div className="text-4xl mb-3" aria-hidden="true">
                    {agent.emoji}
                  </div>
                  
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {agent.name}
                  </h3>
                  
                  <p className="text-sm text-primary-600 mb-3">
                    {agent.role}
                  </p>
                  
                  <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium mb-3 ${
                    agent.score === 'APPROVED' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-primary-100 text-primary-800'
                  }`}>
                    {agent.score}
                  </div>
                  
                  <p className="text-gray-600 text-sm">
                    "{agent.message}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Next Steps */}
        <section className="py-16 bg-white">
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
        <section className="py-16 bg-primary-600">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Share Your Success!
            </h2>
            <p className="text-primary-100 text-lg mb-8">
              You've just experienced the future of loan applications. 
              Share this moment with friends and family!
            </p>
            
            <div className="space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
              <button
                onClick={() => {
                  // Mock social sharing
                  alert('🎉 Shared: "Just got approved for my dream home loan with AI specialists in 15 minutes! The future is here! #LoanAvengers"');
                }}
                className="bg-white text-primary-600 hover:bg-gray-100 font-medium px-6 py-3 rounded-lg transition-colors w-full sm:w-auto"
              >
                📱 Share on Social Media
              </button>
              
              <Link
                to="/"
                className="bg-primary-700 hover:bg-primary-800 text-white font-medium px-6 py-3 rounded-lg transition-colors inline-block w-full sm:w-auto"
              >
                🏠 Back to Home
              </Link>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}