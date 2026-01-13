# Troubleshooting Guide

Solutions to common issues encountered with AI Memory Service.

## Quick Diagnostics

Run these commands to identify issues:

```bash
# 1. Check environment
python3 -c "import config; print('✅ Config loaded')"

# 2. Check AWS credentials
python3 scripts/check_aws_credentials.py

# 3. Check backend health
curl http://localhost:8182/health | python3 -m json.tool

# 4. Check processes
ps aux | grep -E "python3 main|npm.*dev"

# 5. Check ports
lsof -ti:8182  # Backend
lsof -ti:5173  # Frontend
```

---

## Backend Issues

### Error: Missing required environment variables

**Symptoms:**
```
ERROR: Missing required environment variables!
❌ MONGODB_URI (MongoDB Atlas connection string)
❌ AWS_ACCESS_KEY_ID (AWS Access Key ID for Bedrock access)
```

**Solutions:**

1. Create `.env` file if missing:
```bash
cp .env.example .env
```

2. Verify `.env` exists in root directory:
```bash
ls -la .env
```

3. Check file has required variables:
```bash
cat .env | grep -E "^MONGODB_URI|^AWS_"
```

4. Ensure no spaces around `=`:
```bash
# WRONG
MONGODB_URI = mongodb+srv://...

# CORRECT
MONGODB_URI=mongodb+srv://...
```

---

### Error: Port 8182 already in use

**Symptoms:**
```
ERROR: Address already in use
OSError: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8182)
```

**Solutions:**

```bash
# Option 1: Kill process on port
lsof -ti:8182 | xargs kill -9

# Option 2: Kill by name
pkill -9 -f "python3 main.py"

# Option 3: Find and kill manually
lsof -i:8182
kill -9 <PID>

# Then restart
python3 main.py
```

---

### Error: MongoDB connection timeout

**Symptoms:**
```
pymongo.errors.ServerSelectionTimeoutError: 
[Errno 60] Operation timed out, Timeout: 30s
```

**Causes & Solutions:**

**1. Cluster is paused (free tier auto-pauses after 60 days)**
- Go to MongoDB Atlas
- Click "Resume" on your cluster
- Wait 2-3 minutes

**2. IP not whitelisted**
```bash
# Get your public IP
curl ifconfig.me

# Add to MongoDB Atlas:
# Network Access → Add IP Address → Enter IP
```

**3. Wrong connection string**
```bash
# Check format:
mongodb+srv://username:password@cluster.mongodb.net/

# Common mistakes:
# ❌ mongodb:// instead of mongodb+srv://
# ❌ Missing credentials
# ❌ Special chars not URL-encoded in password
```

**4. Network/firewall blocking**
```bash
# Test DNS resolution
nslookup your-cluster.mongodb.net

# Test connectivity
ping your-cluster.mongodb.net
```

---

### Error: AWS Bedrock unavailable

**Symptoms:**
```json
{
  "dependencies": {
    "aws_bedrock": "unavailable"
  }
}
```

**Causes & Solutions:**

**1. Credentials invalid or expired**
```bash
# Test credentials
python3 scripts/check_aws_credentials.py

# If using SSO (expired), refresh:
python3 scripts/refresh_aws_credentials.py

# If using IAM user, check .env:
# - Remove AWS_SESSION_TOKEN line if present
# - Verify access key and secret key
```

**2. Model access not enabled**
- Go to AWS Bedrock Console
- Click "Model access"
- Verify status: "Access granted" for:
  - Amazon Titan Embeddings G1 - Text
  - Claude 3.5 Sonnet

**3. Wrong region**
```bash
# Check .env:
AWS_REGION=us-east-1  # Must be us-east-1

# Some models only available in specific regions
```

**4. IAM permissions missing**
- Go to IAM → Users → Your user
- Verify policy attached: `AmazonBedrockFullAccess`
- Or custom policy with `bedrock:InvokeModel`

---

### Error: UnrecognizedClientException

**Symptoms:**
```
botocore.exceptions.ClientError: An error occurred (UnrecognizedClientException) 
when calling the InvokeModel operation: The security token included in the request is invalid
```

**Root cause:** Using IAM user credentials WITH a session token

**Solution:**
```bash
# Edit .env and remove or comment out:
# AWS_SESSION_TOKEN=...

# Session tokens are ONLY for AWS SSO/temporary credentials
# IAM users don't use session tokens
```

**Verify:**
```bash
# .env should look like:
AWS_ACCESS_KEY_ID=AKIA...          # IAM starts with AKIA
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
# NO session token line

# Restart backend
pkill -f "python3 main.py"
python3 main.py
```

---

### Error: Circular import

**Symptoms:**
```
AttributeError: partially initialized module 'config' has no attribute 'APP_NAME'
```

**Cause:** Import order issue in Python modules

**Solution:** Already fixed in codebase. If you encounter:
1. Check no direct imports of `logger` in `config.py` or `env_validator.py`
2. Verify import order in your code
3. Restart Python process completely

---

## Frontend Issues

### Error: Port 5173 already in use

**Symptoms:**
```
EADDRINUSE: address already in use :::5173
```

**Solutions:**
```bash
# Kill process on port
lsof -ti:5173 | xargs kill -9

# Or change port in vite.config.ts:
server: {
  port: 5174  # Use different port
}
```

---

### Error: Cannot find module errors

**Symptoms:**
```
Failed to resolve import "@radix-ui/react-dialog"
Cannot find module 'class-variance-authority'
```

**Solutions:**
```bash
cd figmaUI

# Option 1: Install missing packages
npm install

# Option 2: Clean install
rm -rf node_modules package-lock.json
npm install

# Option 3: Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

### Error: CORS errors in browser

**Symptoms:**
```
Access to fetch at 'http://localhost:8182/health' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Causes & Solutions:**

**1. Backend not running**
```bash
# Start backend
python3 main.py
```

**2. Wrong API URL in frontend**
```bash
# Check figmaUI/.env.local:
VITE_API_BASE_URL=http://localhost:8182

# Should match backend port
```

**3. Backend CORS not configured**
- Check `config.py` has correct CORS_ORIGINS
- Verify includes `http://localhost:5173`
- Restart backend after changes

---

### Error: Network error / Failed to fetch

**Symptoms:**
- Frontend shows "Offline" or red health indicator
- Console: `TypeError: Failed to fetch`

**Solutions:**
```bash
# 1. Verify backend is running
curl http://localhost:8182/health

# 2. Check frontend env
cat figmaUI/.env.local

# 3. Test from browser directly
# Open: http://localhost:8182/health
# Should see JSON response

# 4. Check backend logs for errors
```

---

## Search/Memory Issues

### Search returns no results

**Symptoms:**
- Search completes but shows "No documents found"
- Memory search finds nothing

**Causes & Solutions:**

**1. Search indexes not created**
```bash
# Check MongoDB Atlas → Search Indexes
# Need 3 indexes (see 03-MONGODB-ATLAS.md):
# 1. conversations_vector_search_index
# 2. conversations_fulltext_search_index
# 3. memory_nodes_vector_search_index

# All must show "Active" status
```

**2. Indexes still building**
- Wait 2-5 minutes after creation
- Check status in Atlas UI
- Won't work until "Active"

**3. No data to search**
```bash
# Send test messages first
curl -X POST http://localhost:8182/conversation/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "conversation_id": "test",
    "type": "human",
    "text": "I love machine learning and AI"
  }'

# Wait 2 seconds for indexing
sleep 2

# Then search
curl "http://localhost:8182/retrieve_memory/?user_id=test&text=AI"
```

**4. Similarity threshold too high**
- App filters results with score < 0.70
- Try exact words from messages
- Check backend logs for pre-filter results

---

### Slow search performance

**Symptoms:**
- Searches take 1-2 seconds or more
- UI feels sluggish

**Root cause:** AWS Bedrock embedding generation on every search

**Solutions:**

See [Advanced Optimizations](07-ADVANCED-OPTIMIZATIONS.md) for:
1. Embedding cache (instant repeated searches)
2. Increased frontend debounce
3. Faster embedding models
4. Local embeddings

**Quick fix:**
```javascript
// figmaUI/app/components/unified-chat.tsx
// Increase debounce from 500ms to 1000ms:
const debouncedSearch = useDebounce(searchQuery, 1000);
```

---

### Memory not being created

**Symptoms:**
- Messages saved successfully
- But no memories appear in dashboard
- Logs show "Memory creation failed"

**Causes & Solutions:**

**1. Bedrock unavailable**
```bash
# Check health
curl http://localhost:8182/health

# Should show:
"aws_bedrock": "available"

# If unavailable, fix AWS credentials
```

**2. Message too short**
```javascript
// Memories only created for messages > 30 characters
// From conversation_service.py:
if message_input.type == "human" and len(message_input.text) > 30:
    # Creates memory
```

**3. Bedrock errors in logs**
- Check backend terminal for errors
- Look for "Memory creation failed"
- Check AWS credentials and model access

---

## Performance Issues

### High latency on all requests

**Symptoms:**
- All API calls slow (3+ seconds)
- Not just search

**Causes & Solutions:**

**1. MongoDB connection slow**
```bash
# Test connection speed
time python3 -c "from database.mongodb import client; client.server_info()"

# Should be < 500ms
# If slow, try different MongoDB region
```

**2. AWS Bedrock latency**
- Cold starts can be slow
- First request always slower
- Consider caching or async processing

**3. Network issues**
- Check internet connection
- Try different network
- Check firewall/VPN

---

### High memory usage

**Symptoms:**
- Python process using excessive RAM
- System slow/swapping

**Causes:**
- Large number of cached embeddings
- MongoDB connection pool

**Solutions:**
```bash
# Restart backend periodically
pkill -f "python3 main.py"
python3 main.py

# Or implement cache limits in code
# (see Advanced Optimizations)
```

---

## Development Issues

### Changes not reflecting

**Frontend:**
```bash
# Vite has hot reload, but sometimes needs restart
cd figmaUI
# Ctrl+C to stop
npm run dev  # Restart

# Or clear cache
rm -rf node_modules/.vite
npm run dev
```

**Backend:**
```bash
# FastAPI auto-reload enabled by default
# But manual restart ensures fresh state
pkill -f "python3 main.py"
python3 main.py
```

---

### Git issues

**Accidentally committed .env:**
```bash
# Remove from git (keeps local file)
git rm --cached .env

# Add to .gitignore
echo ".env" >> .gitignore

# Commit the removal
git commit -m "Remove .env from tracking"

# Rotate your credentials immediately!
# (create new AWS keys, update .env)
```

---

## Getting More Help

### Check Logs

**Backend:**
```bash
# Backend logs are in terminal where you ran:
python3 main.py

# For more detail, set DEBUG=true in .env
```

**Frontend:**
```bash
# Browser console (F12)
# Look for errors, warnings, network failures

# Terminal where you ran:
cd figmaUI && npm run dev
```

**MongoDB:**
- Atlas UI → Database → Logs
- Check for connection issues, slow queries

**AWS:**
- CloudTrail logs in AWS Console
- Bedrock metrics and errors

### Comprehensive Health Check

```bash
# Run validation script (checks everything)
python3 scripts/validate_setup.py

# Should show all ✅ or point to issues
```

### Debug Steps

1. **Isolate the component:**
   - Backend only? Test with curl
   - Frontend only? Check browser console
   - AWS? Test with scripts
   - MongoDB? Test with Compass

2. **Read error messages carefully:**
   - Full error trace
   - Error codes
   - Line numbers

3. **Check recent changes:**
   - What changed before error?
   - New dependencies?
   - Config changes?

4. **Test with clean state:**
   - Fresh terminal
   - Restart services
   - Clear caches

5. **Verify prerequisites:**
   - Python version
   - Node version
   - Package versions

---

## Common Error Patterns

**Import errors** → Run `pip3 install -r requirements.txt` or `npm install`

**Connection errors** → Check service is running, ports correct, network access

**Authentication errors** → Check credentials, permissions, expiration

**Not found errors** → Check names match exactly (case-sensitive!)

**Timeout errors** → Check network, service health, increase timeout

---

**Still stuck?** Review setup guides:
- [Setup Guide](02-SETUP-GUIDE.md)
- [MongoDB Atlas](03-MONGODB-ATLAS.md)
- [AWS Bedrock](04-AWS-BEDROCK.md)
