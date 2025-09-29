import { useState, useEffect } from 'react';

/**
 * Theme toggle component for switching between light and dark modes
 * Inspired by Vite's sophisticated theme switcher
 */
export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check for saved theme preference or default to 'light'
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDark(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);

    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  return (
    <button
      onClick={toggleTheme}
      className="relative inline-flex items-center justify-center w-12 h-11 bg-gray-200 dark:bg-dark-bg-tertiary rounded-full transition-all duration-300 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-vite-purple focus:ring-opacity-50"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {/* Toggle background gradient */}
      <div className="absolute inset-0 rounded-full bg-gradient-to-r from-gray-300 to-gray-400 dark:from-vite-purple dark:to-dark-electric-blue transition-all duration-300"></div>

      {/* Toggle circle */}
      <div
        className={`relative w-5 h-5 bg-white dark:bg-dark-bg-primary rounded-full shadow-md transform transition-all duration-300 flex items-center justify-center ${
          isDark ? 'translate-x-2.5' : '-translate-x-2.5'
        }`}
      >
        {/* Icon */}
        <span className="text-xs">
          {isDark ? '🌙' : '☀️'}
        </span>
      </div>
    </button>
  );
}