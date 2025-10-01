import { Link } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { ExperimentalDisclaimer } from '../../components/ui/ExperimentalDisclaimer';
import { Capabilities } from '../../components/home/Capabilities';
import { ArchitectureDiagram } from '../../components/home/ArchitectureDiagram';

/**
 * Home page component - the landing page for the Loan Avengers application.
 * Showcases Microsoft Agent Framework capabilities and the AI Dream Team.
 */
export function HomePage() {
  const aiTeam = [
    {
      name: 'Cap-ital America',
      role: 'Loan Orchestrator',
      emoji: '🦸‍♂️',
      description: 'Leading your loan journey with unwavering dedication',
    },
    {
      name: 'Scarlet Witch-Credit',
      role: 'Credit Specialist',
      emoji: '🦸‍♀️',
      description: 'Mystically analyzing your credit reality',
    },
    {
      name: 'Hawk-Income',
      role: 'Income Specialist',
      emoji: '🦸',
      description: 'Never missing a detail in income verification',
    },
    {
      name: 'Doctor Strange-Risk',
      role: 'Risk Advisor',
      emoji: '🦹‍♂️',
      description: 'Seeing all possible loan outcomes',
    },
  ];

  return (
    <Layout title="Microsoft Agent Framework - Loan Avengers">
      <div className="animate-fade-in">
        {/* Hero Section */}
        <section className="relative bg-gradient-to-br from-gray-50 via-white to-brand-25 dark:from-dark-bg-primary dark:via-dark-bg-secondary dark:to-dark-bg-tertiary py-20 lg:py-28 overflow-hidden transition-colors duration-300">
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

              <p className="text-xl lg:text-2xl text-gray-600 dark:text-dark-text-secondary mb-10 max-w-4xl mx-auto leading-relaxed transition-colors duration-300">
                <span className="font-semibold text-brand-700 dark:text-brand-400">Showcasing Microsoft Agent Framework</span> and{' '}
                <span className="font-semibold text-accent-700 dark:text-accent-400">Azure AI Foundry</span> with multi-agent loan processing.
                No forms, no waiting – just intelligent AI specialists working together in under 2 minutes.
              </p>

              {/* Compact Team Grid */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto mb-12">
                {aiTeam.map((specialist) => (
                  <div
                    key={specialist.name}
                    className="bg-white/90 dark:bg-dark-bg-card/90 backdrop-blur-md rounded-3xl p-6 text-center group hover:scale-110 hover:shadow-2xl hover:shadow-brand-500/20 transition-all duration-300 border-2 border-gray-200/60 dark:border-gray-700/60 hover:border-brand-400 dark:hover:border-brand-500"
                  >
                    <div className="text-4xl mb-3 group-hover:scale-125 transition-transform duration-300">
                      {specialist.emoji}
                    </div>
                    <h3 className="text-base font-bold text-gray-900 dark:text-dark-text-primary mb-1.5">
                      {specialist.name}
                    </h3>
                    <p className="text-xs text-brand-600 dark:text-brand-400 font-semibold">
                      {specialist.role}
                    </p>
                  </div>
                ))}
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-md mx-auto">
                <Link
                  to="/application"
                  className="btn-primary text-lg px-8 py-4 w-full sm:w-auto shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
                >
                  <span>Try the Demo</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>

                <button
                  onClick={() => document.getElementById('capabilities')?.scrollIntoView({ behavior: 'smooth' })}
                  className="btn-secondary text-lg px-8 py-4 w-full sm:w-auto group"
                >
                  <span>Explore Capabilities</span>
                  <svg className="w-5 h-5 group-hover:translate-y-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Capabilities Section */}
        <div id="capabilities">
          <Capabilities />
        </div>

        {/* Architecture Diagram Section */}
        <ArchitectureDiagram />

        {/* Experimental Disclaimer - Footer */}
        <div className="bg-gray-50 dark:bg-dark-bg-secondary py-4 transition-colors duration-300">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <ExperimentalDisclaimer />
          </div>
        </div>
      </div>
    </Layout>
  );
}