import type { ApiConfig } from '../types';

// Environment configuration for the Loan Defenders frontend
export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000', 10),
    retries: parseInt(import.meta.env.VITE_API_RETRIES || '3', 10),
  } as ApiConfig,
  app: {
    name: 'Loan Defenders',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    environment: import.meta.env.MODE || 'development',
  },
  features: {
    enableVoiceInput: import.meta.env.VITE_ENABLE_VOICE_INPUT === 'true',
    enableRealTimeUpdates: import.meta.env.VITE_ENABLE_REAL_TIME_UPDATES === 'true',
    enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  },
  ui: {
    theme: 'light', // Future: support for dark mode
    animations: {
      enabled: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      duration: {
        fast: 150,
        normal: 300,
        slow: 500,
      },
    },
  },
  accessibility: {
    announceRouteChanges: true,
    skipLinkTarget: 'main-content',
    focusManagement: true,
  },
};

// Validation function to ensure required environment variables are present
export const validateConfig = (): boolean => {
  const requiredEnvVars: string[] = [
    // Add any required environment variables here
  ];

  const missing = requiredEnvVars.filter(
    (envVar) => !import.meta.env[envVar]
  );

  if (missing.length > 0) {
    console.error('Missing required environment variables:', missing);
    return false;
  }

  return true;
};

// Development helper to log configuration (non-sensitive parts only)
export const logConfigInfo = (): void => {
  if (config.app.environment === 'development') {
    console.info('🦸‍♂️ Loan Defenders Configuration:', {
      app: config.app,
      features: config.features,
      ui: config.ui,
      api: {
        baseUrl: config.api.baseUrl,
        timeout: config.api.timeout,
      },
    });
  }
};