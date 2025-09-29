/**
 * Experimental disclaimer component for all pages
 * Explains the demo nature and capabilities being showcased
 */
export function ExperimentalDisclaimer() {
  return (
    <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-lg p-3 mb-6 transition-colors duration-300">
      <div className="flex items-start space-x-2">
        <div className="text-amber-600 dark:text-amber-400 text-sm flex-shrink-0" aria-hidden="true">
          🧪
        </div>
        <div className="text-sm">
          <p className="font-medium text-amber-800 dark:text-amber-200 mb-1">
            Experimental Demo Application
          </p>
          <p className="text-amber-700 dark:text-amber-300 leading-relaxed">
            This is an experimental application that simulates a loan processing workflow,
            demonstrating the capabilities of workflow orchestration and Agent Creation of <strong>Microsoft Agent Framework (Preview)</strong> and
            <strong>Azure AI Foundry</strong> with Azure PaaS service including <strong>Azure Container App</strong>.
            This application does not provide actual loans or credit verification services.
          </p>
        </div>
      </div>
    </div>
  );
}