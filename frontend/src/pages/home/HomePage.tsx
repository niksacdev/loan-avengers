import { Link } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';

/**
 * Home page component - the landing page for the Loan Avengers application.
 * Features the AI Dream Team introduction and call-to-action.
 */
export function HomePage() {
  const aiTeam = [
    {
      name: 'Riley',
      role: 'Loan Orchestrator',
      emoji: '🎭',
      description: 'Your personal guide through the loan process',
    },
    {
      name: 'Sarah',
      role: 'Credit Specialist',
      emoji: '💼',
      description: 'Expert in credit analysis and scoring',
    },
    {
      name: 'Marcus',
      role: 'Income Specialist',
      emoji: '📊',
      description: 'Income verification and employment analysis',
    },
    {
      name: 'Alex',
      role: 'Risk Advisor',
      emoji: '🛡️',
      description: 'Risk assessment and loan optimization',
    },
  ];

  return (
    <Layout title="Meet Your AI Dream Team">
      <div className="animate-fade-in">
        {/* Hero Section */}
        <section className="bg-gradient-to-br from-primary-50 to-secondary-50 py-16 lg:py-24">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="text-6xl mb-6 animate-bounce-gentle" aria-hidden="true">
                🦸‍♂️
              </div>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
                Meet Your AI{' '}
                <span className="text-primary-600">Dream Team</span>
              </h1>
              
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                No more forms. No more waiting. Just conversation with AI specialists 
                who get you the perfect loan in minutes, not hours.
              </p>

              <div className="space-y-4 sm:space-y-0 sm:space-x-4 sm:flex sm:justify-center">
                <Link
                  to="/application"
                  className="btn-primary text-lg px-8 py-4 inline-block w-full sm:w-auto"
                >
                  Start Your Loan Journey
                </Link>
                
                <button
                  onClick={() => document.getElementById('ai-team')?.scrollIntoView({ behavior: 'smooth' })}
                  className="btn-secondary text-lg px-8 py-4 w-full sm:w-auto"
                >
                  Meet the Team
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* AI Team Section */}
        <section id="ai-team" className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Your Personal AI Specialists
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Each specialist brings unique expertise to ensure you get the best loan possible.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {aiTeam.map((specialist, index) => (
                <div
                  key={specialist.name}
                  className="card text-center hover:shadow-lg transition-shadow animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="text-4xl mb-4" aria-hidden="true">
                    {specialist.emoji}
                  </div>
                  
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {specialist.name}
                  </h3>
                  
                  <p className="text-primary-600 font-medium mb-3">
                    {specialist.role}
                  </p>
                  
                  <p className="text-gray-600 text-sm">
                    {specialist.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Why Choose Loan Avengers?
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-5xl mb-4" aria-hidden="true">⚡</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Lightning Fast
                </h3>
                <p className="text-gray-600">
                  Get loan decisions in under 2 minutes, not 24-48 hours
                </p>
              </div>

              <div className="text-center">
                <div className="text-5xl mb-4" aria-hidden="true">💬</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Conversational
                </h3>
                <p className="text-gray-600">
                  Chat naturally with AI - no complex forms to fill out
                </p>
              </div>

              <div className="text-center">
                <div className="text-5xl mb-4" aria-hidden="true">🎯</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Personalized
                </h3>
                <p className="text-gray-600">
                  Each specialist focuses on your unique financial situation
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-primary-600">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Meet Your Dream Team?
            </h2>
            <p className="text-primary-100 text-lg mb-8 max-w-2xl mx-auto">
              Join thousands who've transformed their loan experience from anxiety to excitement.
            </p>
            
            <Link
              to="/application"
              className="bg-white text-primary-600 hover:bg-gray-100 font-medium text-lg px-8 py-4 rounded-lg transition-colors inline-block"
            >
              Start Your Application Now
            </Link>
          </div>
        </section>
      </div>
    </Layout>
  );
}