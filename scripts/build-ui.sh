#!/bin/bash
# Build script for frontend UI in monorepo structure

set -e  # Exit on any error

echo "🏗️  Building Loan Avengers UI..."

# Navigate to UI directory
cd loan_avengers/ui

echo "📦 Installing dependencies..."
npm ci

echo "🔍 Running linter..."
npm run lint

echo "🏗️  Building for production..."
npm run build

echo "✅ UI build completed successfully!"
echo "📁 Build output available in loan_avengers/ui/dist/"