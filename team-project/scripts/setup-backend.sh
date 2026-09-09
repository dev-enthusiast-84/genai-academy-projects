#!/bin/bash

# Setup backend dependencies and configuration

set -e

echo "🔧 Setting up backend..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION"

# Create backend directory if needed
mkdir -p backend

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv backend/venv
    echo "✓ Virtual environment created"
fi

# Activate venv and install dependencies
source backend/venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel > /dev/null 2>&1 || true

# Install requirements
if [ -f backend/requirements.txt ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r backend/requirements.txt > /dev/null 2>&1
    echo "✓ Python dependencies installed"
else
    echo "⚠️  backend/requirements.txt not found"
fi

echo "✅ Backend setup complete!"
