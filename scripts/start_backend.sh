#!/bin/bash
# Startup script that checks credentials before starting backend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "============================================================"
echo "Starting AI Memory Service Backend"
echo "============================================================"
echo ""

# Check credentials first
echo "Checking AWS credentials..."
python3 scripts/check_aws_credentials.py

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Credentials are invalid or expired"
    echo ""
    read -p "Would you like to refresh credentials now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        python3 scripts/refresh_aws_credentials.py
        echo ""
        echo "Restarting credential check..."
        python3 scripts/check_aws_credentials.py
        if [ $? -ne 0 ]; then
            echo ""
            echo "❌ Credentials still invalid. Please fix manually."
            exit 1
        fi
    else
        echo ""
        echo "⚠️  Starting backend with invalid credentials"
        echo "   AI features may not work"
        echo ""
    fi
fi

echo ""
echo "Starting backend server..."
echo ""

# Start the backend
python3 main.py
