#!/bin/bash

# Validate configuration is complete and correct

set -e

echo "🔍 Validating configuration..."
echo ""

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "❌ .env.local not found!"
    echo "   Run: make init-env"
    exit 1
fi

# Required variables
REQUIRED_VARS=(
    "ANTHROPIC_API_KEY"
    "SUPABASE_URL"
    "SUPABASE_KEY"
    "PINECONE_API_KEY"
)

# Check each required variable
MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" .env.local; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "❌ Missing required configuration variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "   Edit .env.local and add these values"
    exit 1
fi

# Check if values are actually set (not empty)
source .env.local

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY is empty in .env.local"
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL is empty in .env.local"
    exit 1
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "❌ SUPABASE_KEY is empty in .env.local"
    exit 1
fi

if [ -z "$PINECONE_API_KEY" ]; then
    echo "❌ PINECONE_API_KEY is empty in .env.local"
    exit 1
fi

echo "✅ All required configuration found:"
echo "   ✓ ANTHROPIC_API_KEY configured"
echo "   ✓ SUPABASE_URL configured"
echo "   ✓ SUPABASE_KEY configured"
echo "   ✓ PINECONE_API_KEY configured"

# Optional checks
if command -v docker &> /dev/null; then
    echo "   ✓ Docker installed"
else
    echo "   ⚠️  Docker not found (needed for local development)"
fi

if command -v python3 &> /dev/null; then
    echo "   ✓ Python 3 installed"
else
    echo "   ⚠️  Python 3 not found (needed for backend)"
fi

if command -v node &> /dev/null; then
    echo "   ✓ Node.js installed"
else
    echo "   ⚠️  Node.js not found (needed for frontend)"
fi

echo ""
echo "✅ Configuration validation passed!"
