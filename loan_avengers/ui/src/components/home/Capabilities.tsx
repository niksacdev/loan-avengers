/**
 * Capabilities component - showcases the key technical capabilities
 * of the Microsoft Agent Framework and AI Foundry implementation
 */
export function Capabilities() {
  const capabilities = [
    {
      icon: '🔄',
      title: 'Agent Framework Workflow',
      description: 'Built with Microsoft Agent Framework leveraging Workflows, Agents, and Threads for orchestrated multi-agent collaboration',
      gradient: 'from-vite-purple to-vite-blue',
      features: ['Sequential agent coordination', 'Context-aware processing', 'Real-time state management']
    },
    {
      icon: '🔧',
      title: 'Agent-to-MCP Tools',
      description: 'Seamless integration between AI agents and Model Context Protocol (MCP) servers for specialized tool capabilities',
      gradient: 'from-vite-blue to-brand-500',
      features: ['3 specialized MCP servers', 'Streamable HTTP transport', 'Autonomous tool selection']
    },
    {
      icon: '🔒',
      title: 'Secure Azure Deployment',
      description: 'Production-ready deployment using Azure Container Apps with Entra ID authentication, managed identities, and comprehensive observability across all agents via Microsoft Agent Framework',
      gradient: 'from-brand-500 to-vite-orange',
      features: ['Azure Container Apps', 'Entra ID + Managed Identity', 'Agent Framework observability']
    },
    {
      icon: '🤖',
      title: 'Agents Built by Agents',
      description: 'Revolutionary AI-augmented development using specialized developer agents for architecture, design, and code review - compatible with GitHub Copilot, Claude, and universal AGENTS.md format',
      gradient: 'from-vite-orange to-accent-600',
      features: ['Multi-platform AI support', 'System architecture review', 'Automated code review']
    },
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 via-white to-brand-25 dark:from-dark-bg-primary dark:via-dark-bg-secondary dark:to-dark-bg-tertiary transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center gap-3 px-6 py-3 bg-gradient-to-r from-vite-purple/10 to-vite-orange/10 rounded-full mb-6">
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              POWERED BY MICROSOFT AGENT FRAMEWORK &
            </span>
            <img
              src="/azure-ai-foundry-logo.svg"
              alt="Azure AI Foundry"
              className="h-6 w-6"
            />
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              AZURE AI FOUNDRY
            </span>
          </div>

          <h2 className="text-4xl lg:text-5xl font-black text-gray-900 dark:text-dark-text-primary mb-6 tracking-tight transition-colors duration-300">
            Technical Capabilities
          </h2>

          <p className="text-xl text-gray-600 dark:text-dark-text-secondary max-w-3xl mx-auto leading-relaxed transition-colors duration-300">
            A showcase of cutting-edge AI agent architecture, secure cloud deployment,
            and the revolutionary AI-augmented development workflow
          </p>
        </div>

        {/* Capabilities Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {capabilities.map((capability, index) => (
            <div
              key={capability.title}
              className={`bg-white dark:bg-dark-bg-card rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6 group hover:shadow-2xl dark:hover:shadow-2xl dark:hover:shadow-brand-500/10 transition-all duration-500 animate-fade-in-up animate-stagger-${index + 1} relative`}
            >
              {/* Icon and Title */}
              <div className="flex items-start gap-4 mb-4">
                <div className={`inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br ${capability.gradient} rounded-2xl group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 shadow-lg flex-shrink-0`}>
                  <span className="text-3xl" aria-hidden="true">{capability.icon}</span>
                </div>

                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2 group-hover:text-brand-600 transition-colors duration-300">
                    {capability.title}
                  </h3>
                </div>
              </div>

              {/* Description */}
              <p className="text-gray-700 dark:text-dark-text-secondary leading-relaxed mb-6 transition-colors duration-300">
                {capability.description}
              </p>

              {/* Feature List */}
              <div className="space-y-2">
                {capability.features.map((feature, featureIndex) => (
                  <div key={featureIndex} className="flex items-center gap-2">
                    <div className={`w-1.5 h-1.5 rounded-full bg-gradient-to-r ${capability.gradient}`}></div>
                    <span className="text-sm text-gray-600 dark:text-dark-text-tertiary transition-colors duration-300">
                      {feature}
                    </span>
                  </div>
                ))}
              </div>

              {/* Hover Effect Overlay */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${capability.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500 pointer-events-none`}></div>
            </div>
          ))}
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <a
            href="#architecture"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-vite-purple to-vite-orange text-white font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-300 group"
          >
            <span>View Technical Architecture</span>
            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
}