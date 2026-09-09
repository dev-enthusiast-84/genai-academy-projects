#!/bin/bash

# Setup frontend dependencies and configuration

set -e

echo "🔧 Setting up frontend..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Node.js $NODE_VERSION"

# Create frontend directory if needed
mkdir -p frontend

# Install npm dependencies
if [ -f frontend/package.json ]; then
    echo "📦 Installing Node dependencies..."
    cd frontend
    npm install > /dev/null 2>&1
    echo "✓ Node dependencies installed"
    cd ..
else
    echo "⚠️  frontend/package.json not found"
fi

echo "✅ Frontend setup complete!"
