# Quick Start Guide

Get AI Memory Service running in 5-10 minutes.

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed
- MongoDB Atlas account (free tier works)
- AWS account with Bedrock access

## Setup Steps

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-memory

# Install Python dependencies
pip3 install -r requirements.txt

# Install frontend dependencies
cd figmaUI
npm install
cd ..
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

**Required configuration:**
- `MONGODB_URI` - Get from MongoDB Atlas → Connect
- `AWS_ACCESS_KEY_ID` - Your AWS IAM user access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS IAM user secret key

See [Setup Guide](02-SETUP-GUIDE.md) for detailed instructions.

### 3. Validate Setup

```bash
# Test AWS credentials
python3 scripts/check_aws_credentials.py

# Validate all configuration
python3 scripts/validate_setup.py
```

### 4. Start the Application

**Option A: Use start script (recommended)**
```bash
./scripts/start_demo.sh
```

**Option B: Manual start**

Terminal 1 - Backend:
```bash
python3 main.py
```

Terminal 2 - Frontend:
```bash
cd figmaUI
npm run dev
```

### 5. Open and Test

1. Open browser to **http://localhost:5173**
2. Verify green "Healthy" indicator in top-right
3. Try the demos:

**Chat Demo (Single User):**
- User ID: `alice`
- Conversation ID: `demo_test`
- Message: `I'm building a recommendation engine using machine learning`
- Watch real-time vectorization
- Search for: `AI models` (different words, semantic search!)

**Demo Mode (Multi-User):**
- Click "Demo Mode" tab
- Send messages as Alice, Bob, Carol
- Try global search across all users

**Memories:**
- Click "Memories" tab
- Load memories for `alice`
- See AI-generated summaries and importance scores

## What You're Seeing

### MongoDB Atlas Features
- ✅ Vector search with 1536-dimension embeddings
- ✅ Hybrid search (text + semantic)
- ✅ Cross-user, cross-conversation queries
- ✅ Real-time indexing

### AWS Bedrock Features
- ✅ Titan embeddings generation
- ✅ Claude AI importance assessment
- ✅ Claude AI summarization
- ✅ Real-time processing

## Quick Troubleshooting

**Backend shows `aws_bedrock: unavailable`**
```bash
# Check credentials
python3 scripts/check_aws_credentials.py

# If expired, refresh
python3 scripts/refresh_aws_credentials.py
```

**Search not working**
- MongoDB Atlas Search Indexes need to be created
- See [MongoDB Atlas Guide](03-MONGODB-ATLAS.md)

**Port conflicts**
```bash
# Kill existing processes
pkill -9 -f "python.*main.py"
lsof -ti:8182 | xargs kill -9
```

## Next Steps

- [Detailed Setup Guide](02-SETUP-GUIDE.md) - Complete configuration
- [MongoDB Atlas Setup](03-MONGODB-ATLAS.md) - Search indexes
- [AWS Bedrock Setup](04-AWS-BEDROCK.md) - Model access
- [Troubleshooting](05-TROUBLESHOOTING.md) - Common issues
- [Advanced Optimizations](07-ADVANCED-OPTIMIZATIONS.md) - Performance tuning

## Architecture Overview

```
User Input → FastAPI Backend → MongoDB Atlas (Vector Storage)
                ↓
         AWS Bedrock (Titan + Claude)
                ↓
         Real-time Embeddings + AI Summaries
                ↓
         Semantic Search Results → React Frontend
```

**Stack:**
- Backend: Python, FastAPI, pymongo
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Database: MongoDB Atlas (Vector Search)
- AI: AWS Bedrock (Titan Embeddings, Claude)

## Support

Having issues? Check:
1. [Troubleshooting Guide](05-TROUBLESHOOTING.md)
2. Backend logs for errors
3. Browser console for frontend errors
4. MongoDB Atlas connection status
5. AWS Bedrock model access status

---

**Estimated setup time:** 5-10 minutes (with existing accounts)

**Demo ready:** Immediately after setup completes
