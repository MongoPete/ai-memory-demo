#!/bin/bash
# =============================================================================
# AI Memory Service - Start Demo Script
# =============================================================================
# Starts both backend and frontend in the background
# Use this for quick demos and development
# =============================================================================

set -e  # Exit on error

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
BACKEND_PORT=8182
FRONTEND_PORT=5173
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "   Stopped backend (PID: $BACKEND_PID)"
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "   Stopped frontend (PID: $FRONTEND_PID)"
    fi
    
    echo ""
    echo "✅ Services stopped"
    exit 0
}

check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use (needed for $service)"
        echo ""
        echo "Kill the existing process?"
        echo "  lsof -ti:$port | xargs kill -9"
        echo ""
        read -p "Kill process and continue? (y/N) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
            sleep 2
            echo "✅ Port $port freed"
        else
            echo "❌ Cannot start $service - port in use"
            exit 1
        fi
    fi
}

# -----------------------------------------------------------------------------
# Trap Ctrl+C
# -----------------------------------------------------------------------------
trap cleanup INT TERM

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
echo "============================================================"
echo "🚀 AI Memory Service - Starting Demo"
echo "============================================================"
echo ""

cd "$PROJECT_ROOT"

# -----------------------------------------------------------------------------
# Pre-flight Checks
# -----------------------------------------------------------------------------
echo "📋 Pre-flight checks..."
echo ""

# Check .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo ""
    echo "Run setup first:"
    echo "  ./scripts/quick_setup.sh"
    echo ""
    exit 1
fi

# Check Python packages
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "❌ Python dependencies not installed"
    echo ""
    echo "Run:"
    echo "  pip3 install -r requirements.txt"
    echo ""
    exit 1
fi

# Check Node modules
if [ ! -d "figmaUI/node_modules" ]; then
    echo "❌ Frontend dependencies not installed"
    echo ""
    echo "Run:"
    echo "  cd figmaUI && npm install"
    echo ""
    exit 1
fi

echo "✅ Dependencies OK"
echo ""

# -----------------------------------------------------------------------------
# Check Ports
# -----------------------------------------------------------------------------
echo "🔍 Checking ports..."
echo ""

check_port $BACKEND_PORT "backend"
check_port $FRONTEND_PORT "frontend"

echo "✅ Ports available"
echo ""

# -----------------------------------------------------------------------------
# Optional: Refresh AWS Credentials
# -----------------------------------------------------------------------------
if [ -f "scripts/refresh_aws_credentials.py" ]; then
    # Check if using session token (SSO)
    if grep -q "AWS_SESSION_TOKEN" .env 2>/dev/null; then
        echo "🔑 Checking AWS credentials..."
        
        # Test if credentials work
        if ! python3 scripts/check_aws_credentials.py >/dev/null 2>&1; then
            echo "⚠️  AWS credentials may be expired"
            echo "   Attempting to refresh..."
            
            if command -v aws &> /dev/null; then
                python3 scripts/refresh_aws_credentials.py || {
                    echo "⚠️  Auto-refresh failed"
                    echo "   AWS features may not work"
                    echo "   See docs/04-AWS-BEDROCK.md for help"
                }
            else
                echo "⚠️  AWS CLI not installed, skipping refresh"
                echo "   AWS features may not work if credentials expired"
            fi
        else
            echo "✅ AWS credentials valid"
        fi
        echo ""
    fi
fi

# -----------------------------------------------------------------------------
# Start Backend
# -----------------------------------------------------------------------------
echo "🐍 Starting backend..."
echo "   Port: $BACKEND_PORT"
echo "   Logs: backend.log"
echo ""

python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    echo ""
    echo "Check logs:"
    echo "  tail -50 backend.log"
    echo ""
    cat backend.log
    exit 1
fi

# Test health endpoint
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    echo "✅ Backend running (PID: $BACKEND_PID)"
else
    echo "⚠️  Backend started but health check failed"
    echo "   Continuing anyway..."
fi

echo ""

# -----------------------------------------------------------------------------
# Start Frontend
# -----------------------------------------------------------------------------
echo "⚛️  Starting frontend..."
echo "   Port: $FRONTEND_PORT"
echo "   Logs: frontend.log"
echo ""

cd figmaUI
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

# Check if frontend started
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start"
    echo ""
    echo "Check logs:"
    echo "  tail -50 frontend.log"
    echo ""
    cat frontend.log
    cleanup
    exit 1
fi

echo "✅ Frontend running (PID: $FRONTEND_PID)"
echo ""

# -----------------------------------------------------------------------------
# Success
# -----------------------------------------------------------------------------
echo "============================================================"
echo "✅ Demo Running!"
echo "============================================================"
echo ""
echo "🌐 Frontend:  http://localhost:$FRONTEND_PORT"
echo "🔧 Backend:   http://localhost:$BACKEND_PORT"
echo "❤️  Health:    http://localhost:$BACKEND_PORT/health"
echo "📖 API Docs:  http://localhost:$BACKEND_PORT/docs"
echo ""
echo "============================================================"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop:"
echo "   Press Ctrl+C"
echo "   Or run: pkill -f 'python3 main.py' && pkill -f 'vite'"
echo ""
echo "============================================================"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# -----------------------------------------------------------------------------
# Wait for interrupt
# -----------------------------------------------------------------------------
# Keep script running and monitor processes
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo ""
        echo "❌ Backend process died unexpectedly"
        echo "   Check backend.log for errors"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo ""
        echo "❌ Frontend process died unexpectedly"
        echo "   Check frontend.log for errors"
        cleanup
        exit 1
    fi
    
    sleep 5
done
