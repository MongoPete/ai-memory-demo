#!/bin/bash
# =============================================================================
# AI Memory Service - Quick Setup Script
# =============================================================================
# This script automates the initial setup process
# Run once to install dependencies and validate configuration
# =============================================================================

set -e  # Exit on error

echo "============================================================"
echo "AI Memory Service - Quick Setup"
echo "============================================================"
echo ""

# -----------------------------------------------------------------------------
# Check Prerequisites
# -----------------------------------------------------------------------------
echo "📋 Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js $NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    echo "   Install Node.js from: https://nodejs.org/"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✅ npm $NPM_VERSION found"

echo ""

# -----------------------------------------------------------------------------
# Install Python Dependencies
# -----------------------------------------------------------------------------
echo "📦 Installing Python dependencies..."
echo ""

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    echo "   Are you in the project root directory?"
    exit 1
fi

pip3 install -r requirements.txt > /dev/null 2>&1 || {
    echo "⚠️  pip3 install failed, trying with --user flag..."
    pip3 install --user -r requirements.txt
}

echo "✅ Python dependencies installed"
echo ""

# -----------------------------------------------------------------------------
# Install Frontend Dependencies
# -----------------------------------------------------------------------------
echo "📦 Installing frontend dependencies..."
echo ""

if [ ! -d "figmaUI" ]; then
    echo "❌ figmaUI directory not found"
    exit 1
fi

cd figmaUI
npm install > /dev/null 2>&1
cd ..

echo "✅ Frontend dependencies installed"
echo ""

# -----------------------------------------------------------------------------
# Check Environment Configuration
# -----------------------------------------------------------------------------
echo "⚙️  Checking environment configuration..."
echo ""

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo ""
    
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "✅ .env created"
        echo ""
        echo "❗ IMPORTANT: Edit .env and add your credentials:"
        echo "   - MONGODB_URI (from MongoDB Atlas)"
        echo "   - AWS_ACCESS_KEY_ID"
        echo "   - AWS_SECRET_ACCESS_KEY"
        echo ""
        echo "Then run this script again to validate."
        exit 1
    else
        echo "❌ .env.example not found"
        echo "   Please create .env manually with required credentials"
        exit 1
    fi
fi

echo "✅ .env file exists"
echo ""

# -----------------------------------------------------------------------------
# Validate Configuration
# -----------------------------------------------------------------------------
echo "✓ Validating configuration..."
echo ""

# Quick validation without running full validation script
python3 -c "import config" 2>/dev/null || {
    echo "❌ Configuration validation failed"
    echo ""
    echo "Common issues:"
    echo "  - Missing required environment variables in .env"
    echo "  - MongoDB URI format incorrect"
    echo "  - AWS credentials not set"
    echo ""
    echo "See docs/02-SETUP-GUIDE.md for help"
    exit 1
}

echo "✅ Configuration valid"
echo ""

# -----------------------------------------------------------------------------
# Frontend Environment
# -----------------------------------------------------------------------------
echo "⚙️  Configuring frontend..."
echo ""

if [ ! -f "figmaUI/.env.local" ]; then
    if [ -f "figmaUI/.env.example" ]; then
        cp figmaUI/.env.example figmaUI/.env.local
        echo "✅ Created figmaUI/.env.local"
    else
        echo "VITE_API_BASE_URL=http://localhost:8182" > figmaUI/.env.local
        echo "✅ Created figmaUI/.env.local with defaults"
    fi
else
    echo "✅ figmaUI/.env.local already exists"
fi

echo ""

# -----------------------------------------------------------------------------
# Optional: Check AWS Credentials
# -----------------------------------------------------------------------------
if [ -f "scripts/check_aws_credentials.py" ]; then
    echo "🔑 Testing AWS credentials (optional)..."
    echo ""
    
    python3 scripts/check_aws_credentials.py 2>/dev/null && {
        echo "✅ AWS Bedrock accessible"
    } || {
        echo "⚠️  AWS Bedrock not accessible"
        echo "   This is OK for initial setup"
        echo "   Configure AWS later following docs/04-AWS-BEDROCK.md"
    }
    echo ""
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Verify your .env file has correct credentials:"
echo "   - MONGODB_URI"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo ""
echo "2. Create MongoDB Atlas Search Indexes:"
echo "   See: docs/03-MONGODB-ATLAS.md"
echo ""
echo "3. Start the application:"
echo "   ./scripts/start_demo.sh"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:5173"
echo ""
echo "============================================================"
echo ""
echo "Need help? See docs/01-QUICKSTART.md or docs/05-TROUBLESHOOTING.md"
echo ""
