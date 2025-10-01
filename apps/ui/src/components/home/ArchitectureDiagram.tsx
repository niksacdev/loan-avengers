/**
 * ArchitectureDiagram component - displays a simplified block diagram
 * of the system architecture showing the correct relationships between
 * User Interface, Agent Framework, Azure AI Foundry, MCP Tools, and Azure Foundation
 */
export function ArchitectureDiagram() {
  return (
    <section id="architecture" className="py-20 bg-white dark:bg-dark-bg-secondary transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-black text-gray-900 dark:text-dark-text-primary mb-6 tracking-tight transition-colors duration-300">
            System Architecture
          </h2>
          <p className="text-xl text-gray-600 dark:text-dark-text-secondary max-w-3xl mx-auto leading-relaxed transition-colors duration-300">
            Multi-agent workflow powered by Microsoft Agent Framework and Azure AI Foundry
          </p>
        </div>

        {/* Architecture Layers */}
        <div className="relative max-w-6xl mx-auto space-y-8">

          {/* Layer 1: User Interface */}
          <div className="animate-fade-in-up animate-stagger-1">
            <div className="flex justify-center">
              <div className="bg-white dark:bg-dark-bg-card rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6 w-full max-w-md">
                <div className="flex items-center gap-3 mb-2">
                  <div className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-br from-brand-400 to-brand-600 rounded-lg">
                    <span className="text-xl">👤</span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-dark-text-primary">User Interface</h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-dark-text-secondary">React 19 + TypeScript with real-time updates</p>
              </div>
            </div>
            {/* Down arrow */}
            <div className="flex justify-center mt-4">
              <svg className="w-6 h-6 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>
          </div>

          {/* Layer 2: Agent Framework + AI Foundry (Side by Side with Bidirectional) */}
          <div className="animate-fade-in-up animate-stagger-2">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

              {/* Microsoft Agent Framework */}
              <div className="bg-white dark:bg-dark-bg-card rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6 bg-gradient-to-br from-vite-purple/5 to-vite-orange/5 dark:from-dark-electric-purple/10 dark:to-dark-electric-orange/10">
                <div className="flex items-center gap-2 mb-4">
                  <div className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-br from-vite-purple to-vite-blue rounded-xl">
                    <span className="text-xl">🦸‍♂️</span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-dark-text-primary">Microsoft Agent Framework</h3>
                </div>

                {/* Sequential Agents */}
                <div className="grid grid-cols-2 gap-3 mb-3">
                  {[
                    { emoji: '🦸‍♂️', name: 'Cap-ital America', role: 'Coordinator' },
                    { emoji: '🦸‍♀️', name: 'Scarlet Witch-Credit', role: 'Credit' },
                    { emoji: '🦸', name: 'Hawk-Income', role: 'Income' },
                    { emoji: '🦹‍♂️', name: 'Doctor Strange-Risk', role: 'Risk' },
                  ].map((agent) => (
                    <div key={agent.name} className="bg-white dark:bg-dark-bg-tertiary rounded-lg p-2 text-center">
                      <div className="text-xl mb-1">{agent.emoji}</div>
                      <div className="text-xs font-semibold text-gray-900 dark:text-dark-text-primary">{agent.name}</div>
                      <div className="text-xs text-gray-500 dark:text-dark-text-tertiary">{agent.role}</div>
                    </div>
                  ))}
                </div>

                <div className="text-center">
                  <span className="inline-flex items-center gap-2 px-2 py-1 bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 rounded-full text-xs font-medium">
                    Workflows, Agents & Threads
                  </span>
                </div>
              </div>

              {/* Azure AI Foundry */}
              <div className="bg-white dark:bg-dark-bg-card rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <div className="inline-flex items-center justify-center w-10 h-10 bg-white dark:bg-dark-bg-tertiary rounded-lg p-2">
                    <img
                      src="/azure-ai-foundry-logo.svg"
                      alt="Azure AI Foundry"
                      className="w-full h-full"
                    />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-dark-text-primary">Azure AI Foundry</h3>
                </div>

                <div className="space-y-3">
                  <div className="bg-gray-50 dark:bg-dark-bg-tertiary rounded-lg p-3">
                    <div className="text-sm font-semibold text-gray-900 dark:text-dark-text-primary mb-1">Foundry Model Catalogue</div>
                    <div className="text-xs text-gray-600 dark:text-dark-text-secondary">Agent reasoning & responses</div>
                  </div>
                  <div className="bg-gray-50 dark:bg-dark-bg-tertiary rounded-lg p-3">
                    <div className="text-sm font-semibold text-gray-900 dark:text-dark-text-primary mb-1">Secure Connections</div>
                    <div className="text-xs text-gray-600 dark:text-dark-text-secondary">Managed endpoints & API keys</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Bidirectional Arrow */}
            <div className="flex justify-center items-center my-2 lg:hidden">
              <div className="flex items-center gap-2 text-brand-500 dark:text-brand-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                </svg>
                <span className="text-xs font-medium">Bidirectional</span>
              </div>
            </div>

            {/* Down arrow */}
            <div className="flex justify-center mt-4">
              <svg className="w-6 h-6 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>
          </div>

          {/* Layer 3: MCP Tool Servers */}
          <div className="animate-fade-in-up animate-stagger-3">
            <div className="bg-white dark:bg-dark-bg-card rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6 bg-gradient-to-br from-accent-50 to-success-50 dark:from-dark-bg-tertiary dark:to-dark-bg-tertiary">
              <div className="flex items-center justify-center gap-2 mb-4">
                <div className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-br from-accent-500 to-success-500 rounded-xl">
                  <span className="text-xl">🔧</span>
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-dark-text-primary">MCP Tool Servers</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                {[
                  { icon: '🔍', name: 'Application Verification', port: '8010' },
                  { icon: '📄', name: 'Document Processing', port: '8011' },
                  { icon: '💰', name: 'Financial Calculations', port: '8012' },
                ].map((server) => (
                  <div key={server.name} className="bg-white dark:bg-dark-bg-secondary rounded-lg p-3 text-center">
                    <div className="text-2xl mb-2">{server.icon}</div>
                    <div className="text-sm font-semibold text-gray-900 dark:text-dark-text-primary mb-1">{server.name}</div>
                    <div className="text-xs text-gray-500 dark:text-dark-text-tertiary">Port {server.port}</div>
                  </div>
                ))}
              </div>

              <div className="text-center">
                <span className="inline-flex items-center gap-2 px-2 py-1 bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-300 rounded-full text-xs font-medium">
                  <span className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></span>
                  Streamable HTTP Transport
                </span>
              </div>
            </div>

            {/* Down arrow */}
            <div className="flex justify-center mt-4">
              <svg className="w-6 h-6 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>
          </div>

          {/* Layer 4: Azure Foundation + GitHub DevOps */}
          <div className="animate-fade-in-up animate-stagger-4">
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-2xl shadow-lg border border-blue-200/50 dark:border-blue-700/50 p-6">
              <div className="text-center mb-6">
                <div className="inline-flex items-center gap-2 mb-2">
                  <span className="text-3xl">☁️</span>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-dark-text-primary">Microsoft Azure</h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-dark-text-secondary">Secure & Scalable Foundation</p>
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                {[
                  { icon: '📦', name: 'Azure Container Apps', desc: 'Serverless containers' },
                  { icon: '🔐', name: 'Entra ID', desc: 'Identity & access' },
                  { icon: '🌐', name: 'Application Gateway', desc: 'Load balancing' },
                  { icon: '📊', name: 'Application Insights', desc: 'Observability' },
                  { icon: '🔄', name: 'GitHub DevOps', desc: 'CI/CD pipeline' },
                ].map((service) => (
                  <div key={service.name} className="bg-white dark:bg-dark-bg-card rounded-lg p-3 text-center hover:shadow-md transition-shadow duration-300">
                    <div className="text-2xl mb-2">{service.icon}</div>
                    <div className="text-xs font-semibold text-gray-900 dark:text-dark-text-primary mb-1">{service.name}</div>
                    <div className="text-xs text-gray-500 dark:text-dark-text-tertiary">{service.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Link to Full Documentation */}
        <div className="mt-16 text-center">
          <a
            href="https://github.com/niksacdev/loan-avengers/blob/main/docs/diagrams/system-architecture-diagram.md"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 font-semibold group transition-colors duration-300"
          >
            <span>View Complete Technical Architecture</span>
            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
}