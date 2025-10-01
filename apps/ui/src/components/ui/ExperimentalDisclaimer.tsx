/**
 * Experimental disclaimer component for all pages
 * Explains the demo nature and capabilities being showcased
 */
export function ExperimentalDisclaimer() {
  return (
    <div className="bg-amber-50 dark:bg-amber-900/20 border-t border-amber-200 dark:border-amber-800/50 rounded-none px-4 py-3 transition-colors duration-300">
      <div className="flex items-center justify-center gap-3">
        <div className="text-amber-600 dark:text-amber-400 text-sm flex-shrink-0" aria-hidden="true">
          🧪
        </div>
        <p className="text-xs text-amber-800 dark:text-amber-200 text-center">
          <span className="font-semibold">Experimental Demo Application</span> — This simulates a loan processing workflow and does not provide actual loans or credit verification services.
        </p>
      </div>
    </div>
  );
}