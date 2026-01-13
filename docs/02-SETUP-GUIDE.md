# Complete Setup Guide

Detailed instructions for setting up AI Memory Service from scratch.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [MongoDB Atlas Setup](#mongodb-atlas-setup)
3. [AWS Bedrock Setup](#aws-bedrock-setup)
4. [Application Configuration](#application-configuration)
5. [Running the Application](#running-the-application)
6. [Verification](#verification)

---

## System Requirements

### Required Software
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher
- **Git**: Any recent version

### Check Your Versions
```bash
python3 --version  # Should be 3.10+
node --version     # Should be v18+
npm --version      # Should be 9+
```

### Cloud Accounts Needed
- **MongoDB Atlas**: Free M0 cluster (512MB) is sufficient
- **AWS Account**: With Bedrock access (pay-per-use)

---

## MongoDB Atlas Setup

### Step 1: Create Cluster

1. Go to https://cloud.mongodb.com
2. Sign up or log in
3. Click "Build a Database"
4. Choose **M0 Free** tier
5. Select cloud provider and region (AWS us-east-1 recommended)
6. Name your cluster (e.g., `ai-memory-cluster`)
7. Click "Create"

### Step 2: Create Database User

1. Go to "Database Access" in left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Username: `ai_memory_user` (or your choice)
5. Generate a secure password (save it!)
6. User Privileges: "Atlas admin" or "Read and write to any database"
7. Click "Add User"

### Step 3: Whitelist IP Address

1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. For testing: Click "Allow Access from Anywhere" (0.0.0.0/0)
4. For production: Add your specific IP
5. Click "Confirm"

### Step 4: Get Connection String

1. Go to "Database" in left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Driver: Python, Version: 3.12 or later
5. Copy the connection string
6. It looks like:
   ```
   mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
7. Replace `<username>` and `<password>` with your actual credentials

### Step 5: Create Search Indexes

**Important:** The application needs 3 search indexes to function properly.

1. Click "Browse Collections" on your cluster
2. If database `ai_memory` doesn't exist, it will be created on first message
3. Once you see collections, follow [MongoDB Atlas Guide](03-MONGODB-ATLAS.md) for index creation

---

## AWS Bedrock Setup

### Option A: IAM User (Recommended for Development)

**Step 1: Create IAM User**

1. Go to AWS Console → IAM
2. Click "Users" → "Add users"
3. User name: `ai-memory-bedrock-user`
4. Click "Next"

**Step 2: Attach Permissions**

1. Click "Attach policies directly"
2. Search for `AmazonBedrockFullAccess`
3. Select it
4. Click "Next" → "Create user"

**Step 3: Create Access Key**

1. Click on the user you just created
2. Go to "Security credentials" tab
3. Scroll to "Access keys"
4. Click "Create access key"
5. Use case: "Application running outside AWS"
6. Click "Next" → "Create access key"
7. **Save both values:**
   - Access key ID (starts with `AKIA...`)
   - Secret access key (long string, shown only once!)
8. Download `.csv` file as backup

**Step 4: Enable Bedrock Models**

1. Go to AWS Bedrock console
2. Click "Model access" in left sidebar
3. Click "Manage model access"
4. Enable these models:
   - ✅ Amazon Titan Embeddings G1 - Text
   - ✅ Claude 3.5 Sonnet (or your preferred Claude version)
5. Click "Request model access"
6. Wait for approval (usually instant)

### Option B: AWS SSO (For Enterprise)

If your organization uses AWS SSO:

```bash
# Configure SSO
aws configure sso

# Login
aws sso login

# Get credentials
aws configure export-credentials --format env
```

Add the output to your `.env` file.

---

## Application Configuration

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd ai-memory
```

### Step 2: Create Environment File

```bash
cp .env.example .env
```

### Step 3: Edit Configuration

Open `.env` in your text editor:

```bash
nano .env
# or
code .env
# or
vim .env
```

### Step 4: Fill in Required Values

```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# AWS Bedrock - IAM User
AWS_ACCESS_KEY_ID=AKIA...your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Models (these defaults should work)
LLM_MODEL_ID=arn:aws:bedrock:us-east-1:979559056307:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
```

**Important Notes:**
- Do NOT include `AWS_SESSION_TOKEN` for IAM users
- Session tokens are only for AWS SSO/temporary credentials
- Replace `username` and `password` in MongoDB URI
- Keep your `.env` file secure (never commit to git)

### Step 5: Frontend Configuration

```bash
cd figmaUI
cp .env.example .env.local
```

Edit `figmaUI/.env.local`:
```bash
VITE_API_BASE_URL=http://localhost:8182
```

---

## Running the Application

### Method 1: Using Start Script (Easiest)

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start both backend and frontend
./scripts/start_demo.sh
```

### Method 2: Manual Start

**Terminal 1 - Backend:**
```bash
# Install dependencies (first time only)
pip3 install -r requirements.txt

# Start backend
python3 main.py
```

**Terminal 2 - Frontend:**
```bash
# Install dependencies (first time only)
cd figmaUI
npm install

# Start frontend
npm run dev
```

### Method 3: Using Quick Setup Script

```bash
# Run full setup (first time)
./scripts/quick_setup.sh

# Then start
./scripts/start_demo.sh
```

---

## Verification

### Step 1: Check Backend Health

```bash
curl http://localhost:8182/health | python3 -m json.tool
```

**Expected output:**
```json
{
    "status": "healthy",
    "service": "AI-Memory-Service",
    "version": "1.0",
    "dependencies": {
        "mongodb": "connected",
        "aws_bedrock": "available"
    }
}
```

**If you see issues:**
- `mongodb: "disconnected"` → Check MongoDB URI and network access
- `aws_bedrock: "unavailable"` → Check AWS credentials and model access

### Step 2: Test Frontend

1. Open http://localhost:5173 in browser
2. Check top-right indicator shows green "Healthy"
3. No console errors in browser DevTools (F12)

### Step 3: Send Test Message

```bash
curl -X POST http://localhost:8182/conversation/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "conversation_id": "test_conv",
    "type": "human",
    "text": "I love building recommendation systems with machine learning"
  }' | python3 -m json.tool
```

**Expected:** `{"message": "Message added successfully"}`

### Step 4: Verify Memory Creation

```bash
# Wait 2 seconds for AI processing
sleep 2

# Check memories
curl http://localhost:8182/memories/test_user | python3 -m json.tool
```

**Expected:** JSON array with at least one memory containing:
- AI-generated summary
- Importance score (0-1)
- Access count
- Embeddings array

---

## Common Issues

### MongoDB Connection Timeout

**Error:** `ServerSelectionTimeoutError`

**Solutions:**
1. Check MongoDB cluster is not paused (free tier auto-pauses)
2. Verify IP whitelist includes your current IP
3. Test connection string in MongoDB Compass
4. Check network/firewall not blocking port 27017

### AWS Credentials Invalid

**Error:** `UnrecognizedClientException`

**Solutions:**
1. Verify access key and secret key are correct
2. Remove `AWS_SESSION_TOKEN` if using IAM user
3. Run: `python3 scripts/check_aws_credentials.py`
4. Check IAM user has Bedrock permissions

### Search Not Working

**Error:** No search results or errors in logs

**Solutions:**
1. Create MongoDB Atlas Search Indexes (see [03-MONGODB-ATLAS.md](03-MONGODB-ATLAS.md))
2. Wait 2-5 minutes for indexes to build
3. Verify indexes show "Active" status in Atlas

### Port Already in Use

**Error:** `Address already in use`

**Solutions:**
```bash
# Backend (port 8182)
lsof -ti:8182 | xargs kill -9

# Frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

---

## Next Steps

✅ Setup complete? Try these:

1. **Test all features:**
   - Single user chat
   - Multi-user demo mode
   - Memory dashboard
   - Semantic search

2. **Read advanced guides:**
   - [MongoDB Atlas Details](03-MONGODB-ATLAS.md)
   - [AWS Bedrock Details](04-AWS-BEDROCK.md)
   - [Performance Optimizations](07-ADVANCED-OPTIMIZATIONS.md)

3. **Deploy to production:**
   - [Deployment Guide](06-DEPLOYMENT.md)

4. **Troubleshoot issues:**
   - [Troubleshooting Guide](05-TROUBLESHOOTING.md)

---

**Estimated setup time:** 15-30 minutes for first-time setup

**Questions?** Check the troubleshooting guide or review error messages carefully.
