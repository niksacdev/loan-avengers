# 🦸‍♂️ Loan Avengers Frontend

A React/TypeScript frontend for the revolutionary Loan Avengers conversational loan experience.

## Features

- **React 19** with **TypeScript** for type safety and modern development
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for mobile-first responsive design
- **React Router** for client-side routing
- **Error Boundaries** for graceful error handling
- **Accessibility-first** design with WCAG 2.1 AA compliance
- **Progressive Web App** capabilities

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── layout/          # Layout components (Header, Footer, etc.)
│   ├── ui/             # Reusable UI components
│   └── forms/          # Form components
├── pages/
│   ├── home/           # Home page
│   ├── application/    # Loan application flow
│   ├── results/        # Results and celebration
│   └── error/          # Error pages (404, etc.)
├── services/           # API and external service integrations
├── utils/              # Utility functions and configuration
├── types/              # TypeScript type definitions
└── main.tsx           # Application entry point
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000    # Backend API URL
VITE_API_TIMEOUT=10000                     # Request timeout (ms)
VITE_API_RETRIES=3                         # Number of retries

# Feature Flags
VITE_ENABLE_VOICE_INPUT=false              # Voice input feature
VITE_ENABLE_REAL_TIME_UPDATES=true         # Real-time processing updates
VITE_ENABLE_ANALYTICS=false                # Analytics tracking
```

## Integration with Backend

The frontend connects to the Python backend at `/loan_avengers/`:

- **Agent Communication**: Real-time updates from Cap-ital America, Sarah, Marcus, and Alex
- **Processing Status**: Live progress tracking during loan assessment
- **Document Upload**: Integration with document processing MCP servers
- **Results Display**: Formatted loan decisions and celebrations

## Development Commands

```bash
# Development
npm run dev              # Start dev server with hot reload
npm run build           # Build for production
npm run preview         # Preview production build locally
npm run lint            # Run ESLint
```

---

**Part of the Loan Avengers ecosystem** 🦸‍♂️