import { useState } from 'react';

interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'DEBUG' | 'WARNING' | 'ERROR';
  logger: string;
  message: string;
  extra?: Record<string, any>;
}

interface LogViewerProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string | null;
}

/**
 * Geeky Log Viewer - Shows detailed system logs for debugging
 */
export function LogViewer({ isOpen, onClose, sessionId }: LogViewerProps) {
  const [logs] = useState<LogEntry[]>([]);

  if (!isOpen) return null;

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR':
        return 'text-red-500 dark:text-red-400';
      case 'WARNING':
        return 'text-yellow-500 dark:text-yellow-400';
      case 'DEBUG':
        return 'text-purple-500 dark:text-purple-400';
      default:
        return 'text-blue-500 dark:text-blue-400';
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-2/5 bg-gray-900 text-green-400 font-mono text-xs shadow-2xl z-50 flex flex-col border-l-4 border-green-500">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-950 border-b border-green-500">
        <div className="flex items-center space-x-2">
          <span className="text-green-400 text-lg">🤓</span>
          <h3 className="text-green-400 font-bold">Geek Mode: System Logs</h3>
        </div>
        <button
          onClick={onClose}
          className="text-green-400 hover:text-green-300 transition-colors"
          aria-label="Close log viewer"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Session Info */}
      {sessionId && (
        <div className="px-4 py-2 bg-gray-950 border-b border-gray-800 text-gray-400">
          <span className="text-green-500">Session:</span> {sessionId}
        </div>
      )}

      {/* Logs Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {logs.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>🔍 No logs yet</p>
            <p className="text-xs mt-2">Logs will appear here as the system processes your request</p>
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="border-l-2 border-gray-700 pl-3 py-1 hover:bg-gray-800 transition-colors">
              {/* Timestamp and Level */}
              <div className="flex items-center space-x-2 mb-1">
                <span className="text-gray-500">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                <span className={`font-bold ${getLevelColor(log.level)}`}>{log.level}</span>
                <span className="text-cyan-400">{log.logger}</span>
              </div>

              {/* Message */}
              <div className="text-gray-300 ml-4">{log.message}</div>

              {/* Extra Data */}
              {log.extra && Object.keys(log.extra).length > 0 && (
                <details className="ml-4 mt-1">
                  <summary className="text-yellow-500 cursor-pointer hover:text-yellow-400">
                    📊 Extra Data
                  </summary>
                  <pre className="text-xs text-gray-400 mt-1 p-2 bg-gray-950 rounded overflow-x-auto">
                    {JSON.stringify(log.extra, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-950 border-t border-gray-800 text-gray-500 text-center">
        <span className="text-green-500">⚡</span> Real-time system logs
      </div>
    </div>
  );
}
