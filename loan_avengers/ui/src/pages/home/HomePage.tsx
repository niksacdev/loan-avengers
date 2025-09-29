import { Link } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { ExperimentalDisclaimer } from '../../components/ui/ExperimentalDisclaimer';

/**
 * Home page component - the landing page for the Loan Avengers application.
 * Features the AI Dream Team introduction and call-to-action.
 */
export function HomePage() {
  const aiTeam = [
    {
      name: 'Riley',
      role: 'Loan Orchestrator',
      emoji: '🦸‍♂️',
      description: 'Your personal guide through the loan process',
    },
    {
      name: 'Sarah',
      role: 'Credit Specialist',
      emoji: '🦸‍♀️',
      description: 'Expert in credit analysis and scoring',
    },
    {
      name: 'Marcus',
      role: 'Income Specialist',
      emoji: '🦸',
      description: 'Income verification and employment analysis',
    },
    {
      name: 'Alex',
      role: 'Risk Advisor',
      emoji: '🦹‍♂️',
      description: 'Risk assessment and loan optimization',
    },
  ];

  return (
    <Layout title="Meet Your AI Dream Team">
      <div className="animate-fade-in">
        {/* Experimental Disclaimer */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <ExperimentalDisclaimer />
        </div>
        {/* Hero Section */}
        <section className="relative bg-gradient-to-br from-gray-50 via-white to-brand-25 dark:from-dark-bg-primary dark:via-dark-bg-secondary dark:to-dark-bg-tertiary py-20 lg:py-32 overflow-hidden transition-colors duration-300">
          {/* Complex layered background decoration */}
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-vite-purple/10 via-vite-blue/5 to-transparent dark:from-dark-electric-purple/15 dark:via-dark-electric-blue/10 dark:to-transparent"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-vite-orange/8 via-transparent to-vite-blue/5 dark:from-dark-electric-orange/12 dark:to-dark-electric-blue/8"></div>
          <div className="absolute inset-0 bg-grid-gray-900/[0.02] dark:bg-grid-white/[0.02] bg-[size:20px_20px]"></div>

          {/* Vite-inspired floating orbs */}
          <div className="absolute top-20 left-1/4 w-64 h-64 bg-gradient-to-r from-vite-purple/10 to-vite-blue/10 rounded-full blur-3xl animate-pulse" style={{animationDuration: '8s'}}></div>
          <div className="absolute bottom-20 right-1/4 w-48 h-48 bg-gradient-to-r from-vite-orange/15 to-vite-purple/10 rounded-full blur-2xl animate-pulse" style={{animationDuration: '6s', animationDelay: '2s'}}></div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-8">
                <div className="relative inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-500 via-brand-600 to-accent-600 rounded-xl shadow-lg animate-bounce-gentle">
                  <span className="text-2xl" aria-hidden="true">🦸‍♂️</span>
                  <div className="absolute -inset-1 bg-gradient-to-r from-brand-400 to-accent-500 rounded-xl blur-sm opacity-20 animate-pulse"></div>
                </div>
                <div className="relative inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-accent-500 via-accent-600 to-brand-600 rounded-xl shadow-lg animate-bounce-gentle" style={{animationDelay: '0.2s'}}>
                  <span className="text-2xl" aria-hidden="true">🦸‍♀️</span>
                  <div className="absolute -inset-1 bg-gradient-to-r from-accent-400 to-brand-500 rounded-xl blur-sm opacity-20 animate-pulse delay-200"></div>
                </div>
                <div className="relative inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-success-500 via-success-600 to-brand-600 rounded-xl shadow-lg animate-bounce-gentle" style={{animationDelay: '0.4s'}}>
                  <span className="text-2xl" aria-hidden="true">🦸</span>
                  <div className="absolute -inset-1 bg-gradient-to-r from-success-400 to-brand-500 rounded-xl blur-sm opacity-20 animate-pulse delay-500"></div>
                </div>
                <div className="relative inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-warning-500 via-warning-600 to-brand-600 rounded-xl shadow-lg animate-bounce-gentle" style={{animationDelay: '0.6s'}}>
                  <span className="text-2xl" aria-hidden="true">🦹‍♂️</span>
                  <div className="absolute -inset-1 bg-gradient-to-r from-warning-400 to-brand-500 rounded-xl blur-sm opacity-20 animate-pulse delay-700"></div>
                </div>
              </div>

              <h1 className="text-6xl sm:text-7xl lg:text-8xl font-black tracking-tighter text-gray-900 dark:text-dark-text-primary mb-8 leading-tight transition-colors duration-300">
                Meet the{' '}
                <span className="relative inline-block">
                  <span className="bg-gradient-to-r from-vite-purple via-brand-500 to-vite-orange bg-clip-text text-transparent animate-pulse">
                    Loan Avengers
                  </span>
                  {/* Sophisticated accent effects */}
                  <span className="absolute -top-3 -right-3 text-3xl opacity-80 animate-pulse delay-100">⚡</span>
                  <span className="absolute -bottom-2 -left-2 text-xl opacity-70 animate-bounce delay-200">🚀</span>
                  <span className="absolute top-1/2 -right-6 text-lg opacity-60 animate-ping delay-400">💥</span>
                </span>
              </h1>

              <p className="text-xl lg:text-2xl text-gray-600 mb-10 max-w-4xl mx-auto leading-relaxed">
                <span className="font-semibold text-brand-700">Super-speed loan processing</span> meets <span className="font-semibold text-accent-700">superhuman intelligence</span>.
                No forms, no waiting – just heroic AI specialists who get you approved in minutes, not days.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-md mx-auto">
                <Link
                  to="/application"
                  className="btn-primary text-lg px-8 py-4 w-full sm:w-auto shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
                >
                  <span>Start Your Journey</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>

                <button
                  onClick={() => document.getElementById('ai-team')?.scrollIntoView({ behavior: 'smooth' })}
                  className="btn-secondary text-lg px-8 py-4 w-full sm:w-auto group"
                >
                  <span>Meet the Team</span>
                  <svg className="w-5 h-5 group-hover:translate-y-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
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
                Each superhero brings unique powers to ensure you get the best loan possible.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {aiTeam.map((specialist, index) => (
                <div
                  key={specialist.name}
                  className={`agent-card animate-fade-in-up animate-stagger-${index + 1} group hover:scale-105 hover:shadow-2xl hover:shadow-vite-purple/20 transition-all duration-500 cursor-pointer`}
                >
                  <div className="relative inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-100 to-brand-200 rounded-2xl mb-6 group-hover:scale-125 group-hover:rotate-12 transition-all duration-500 group-hover:shadow-lg group-hover:shadow-vite-orange/30">
                    <span className="text-2xl group-hover:scale-110 transition-transform duration-300" aria-hidden="true">
                      {specialist.emoji}
                    </span>

                    {/* Vite-inspired glow effect on hover */}
                    <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-vite-purple to-vite-orange opacity-0 group-hover:opacity-20 transition-opacity duration-500 blur-xl"></div>

                    {/* Electric particles effect */}
                    <div className="absolute -inset-2 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                      <div className="absolute top-0 left-0 w-1 h-1 bg-dark-electric-blue rounded-full animate-ping" style={{animationDelay: '0s'}}></div>
                      <div className="absolute top-2 right-1 w-1 h-1 bg-dark-electric-purple rounded-full animate-ping" style={{animationDelay: '0.2s'}}></div>
                      <div className="absolute bottom-1 left-2 w-1 h-1 bg-dark-electric-pink rounded-full animate-ping" style={{animationDelay: '0.4s'}}></div>
                    </div>
                  </div>

                  <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-brand-700 transition-colors">
                    {specialist.name}
                  </h3>

                  <div className="inline-flex items-center px-3 py-1 bg-brand-100 text-brand-700 rounded-full text-sm font-medium mb-4">
                    {specialist.role}
                  </div>

                  <p className="text-gray-600 text-sm leading-relaxed">
                    {specialist.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-16 bg-gray-50 dark:bg-dark-bg-secondary transition-colors duration-300">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-dark-text-primary mb-4 transition-colors duration-300">
                Why Choose Loan Avengers?
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="card-elevated text-center group hover:scale-[1.02] transition-all duration-300">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-warning-400 to-warning-500 rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-2xl" aria-hidden="true">⚡</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Lightning Fast
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Get loan decisions in under 2 minutes, not 24-48 hours
                </p>
              </div>

              <div className="card-elevated text-center group hover:scale-[1.02] transition-all duration-300">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-400 to-brand-500 rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-2xl" aria-hidden="true">💬</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Conversational
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Chat naturally with AI - no complex forms to fill out
                </p>
              </div>

              <div className="card-elevated text-center group hover:scale-[1.02] transition-all duration-300">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-500 rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-2xl" aria-hidden="true">🎯</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Personalized
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Each specialist focuses on your unique financial situation
                </p>
              </div>

              <div className="card-elevated text-center group hover:scale-[1.02] transition-all duration-300">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-vite-purple to-vite-orange rounded-2xl mb-6 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-2xl" aria-hidden="true">☁️</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-dark-text-primary mb-3 transition-colors duration-300">
                  Built for Scale
                </h3>
                <p className="text-gray-600 dark:text-dark-text-secondary leading-relaxed transition-colors duration-300">
                  Powered by <strong>Microsoft Agent Framework</strong> and <strong>Azure AI Foundry</strong>
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="relative py-20 bg-gradient-to-br from-brand-600 via-brand-700 to-accent-700 overflow-hidden">
          {/* Background decoration */}
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-brand-500/20 via-accent-600/15 to-transparent"></div>
          <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:20px_20px]"></div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6 tracking-tight">
              Ready to Meet Your Dream Team?
            </h2>
            <p className="text-brand-100 text-xl mb-10 max-w-3xl mx-auto leading-relaxed">
              Join thousands who've transformed their loan experience from anxiety to excitement.
            </p>

            <Link
              to="/application"
              className="inline-flex items-center gap-3 bg-white text-brand-600 hover:bg-gray-50 font-semibold text-lg px-10 py-5 rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 group"
            >
              <span>Start Your Application Now</span>
              <svg className="w-6 h-6 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>
        </section>
      </div>
    </Layout>
  );
}