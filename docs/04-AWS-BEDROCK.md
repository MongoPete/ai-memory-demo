# AWS Bedrock Setup

Complete guide for configuring AWS Bedrock for AI Memory Service.

## Overview

AWS Bedrock provides two AI models for this application:
- **Amazon Titan Embeddings** - Generates 1536-dimension vectors from text
- **Anthropic Claude** - Assesses importance and creates summaries

## Prerequisites

- AWS Account
- IAM permissions to create users/roles
- Credit card on file (pay-per-use pricing)

## Setup Methods

Choose one based on your use case:

### Option A: IAM User (Recommended for Development)

**Pros:**
- Permanent credentials
- Simple setup
- No expiration

**Cons:**
- Need to rotate regularly
- Manual credential management

### Option B: AWS SSO (Recommended for Enterprise)

**Pros:**
- Temporary credentials
- Centralized access management
- Auto-expiry for security

**Cons:**
- Requires SSO setup
- Credentials expire (need refresh)
- More complex initial setup

---

## Option A: IAM User Setup

### Step 1: Create IAM User

1. Go to AWS Console → **IAM**
2. Click **Users** → **Create user**
3. User name: `bedrock-ai-memory` (or your choice)
4. Click **Next**

### Step 2: Attach Permissions

**Quick Method (Full Access):**
1. Click "Attach policies directly"
2. Search for: `AmazonBedrockFullAccess`
3. Select it
4. Click **Next** → **Create user**

**Secure Method (Minimal Permissions):**
1. Click "Create policy" (opens new tab)
2. Select JSON editor
3. Paste this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1",
                "arn:aws:bedrock:*:*:inference-profile/*"
            ]
        }
    ]
}
```

4. Name: `BedrockAIMemoryPolicy`
5. Create policy
6. Return to user creation tab
7. Refresh policies list
8. Select `BedrockAIMemoryPolicy`
9. Create user

### Step 3: Create Access Keys

1. Click on your new user
2. Go to **Security credentials** tab
3. Scroll to **Access keys** section
4. Click **Create access key**
5. Use case: "Application running outside AWS"
6. Click **Next**
7. Description: "AI Memory Service" (optional)
8. Click **Create access key**

**⚠️ IMPORTANT:**
- Access key ID: Starts with `AKIA...` (save this)
- Secret access key: Long string (save this - shown ONLY ONCE!)
- Download `.csv` file as backup
- Click **Done**

### Step 4: Add to .env File

```bash
AWS_ACCESS_KEY_ID=AKIA...your_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1

# DO NOT include AWS_SESSION_TOKEN for IAM users!
```

---

## Option B: AWS SSO Setup

### Step 1: Configure SSO

```bash
# Install AWS CLI if not already installed
# brew install awscli  (macOS)
# pip install awscli   (Python)

# Configure SSO
aws configure sso
```

Follow prompts:
- SSO session name: `bedrock-session`
- SSO start URL: Your organization's SSO URL
- SSO region: `us-east-1`
- SSO registration scopes: `sso:account:access`

### Step 2: Login

```bash
aws sso login --profile bedrock-session
```

Browser will open for authentication.

### Step 3: Export Credentials

```bash
# Get temporary credentials
aws configure export-credentials --profile bedrock-session --format env
```

Output looks like:
```bash
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="IQoJ..."
```

### Step 4: Add to .env File

```bash
AWS_ACCESS_KEY_ID=ASIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=IQoJ...  # Include for SSO
AWS_REGION=us-east-1
```

**Note:** SSO credentials expire (typically 1-12 hours). Use the auto-refresh script:
```bash
python3 scripts/refresh_aws_credentials.py
```

---

## Enable Bedrock Model Access

Both options require enabling model access in AWS Bedrock.

### Step 1: Open Bedrock Console

1. Go to AWS Console → **Amazon Bedrock**
2. Select region: **us-east-1** (top-right)
3. Click **Model access** in left sidebar

### Step 2: Request Model Access

1. Click **Manage model access** (orange button)
2. Find and enable these models:
   - ✅ **Amazon Titan Embeddings G1 - Text**
   - ✅ **Claude 3.5 Sonnet** (or latest version)
3. Click **Request model access**

### Step 3: Wait for Approval

- Status will change from "Pending" to "Access granted"
- Usually **instant** for most models
- Some models may require AWS approval (1-2 business days)

### Step 4: Verify Access

```bash
# Test credentials and model access
python3 scripts/check_aws_credentials.py
```

Expected output:
```
============================================================
AWS Credentials Check
============================================================

✅ Access Key ID: AKIA...
✅ Secret Key: ********************
✅ Region: us-east-1

Testing Bedrock access...

✅ Credentials are valid and Bedrock is accessible!
```

---

## Model Configuration

### Current Models

**Embedding Model:**
```bash
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
```
- Generates 1536-dimension vectors
- Cost: ~$0.10 per 1M tokens
- Latency: 500-1500ms

**LLM Model (Claude):**
```bash
LLM_MODEL_ID=arn:aws:bedrock:us-east-1:979559056307:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0
```
- Assesses importance (1-10 scale)
- Generates summaries
- Cost: ~$3 per 1M tokens input, ~$15 per 1M tokens output
- Latency: 1-3 seconds per request

### Alternative Models

**Cohere Embeddings (Faster):**
```bash
EMBEDDING_MODEL_ID=cohere.embed-english-v3
```
- 1024 dimensions (requires index updates)
- 2x faster than Titan
- Different pricing

**Claude Haiku (Cheaper):**
```bash
LLM_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```
- Lower cost
- Slightly lower quality
- Faster responses

---

## Troubleshooting

### UnrecognizedClientException

**Error:** "The security token included in the request is invalid"

**Causes:**
1. **Wrong credentials** - Check access key and secret key
2. **Expired session token** - Refresh SSO credentials
3. **IAM user with session token** - Remove `AWS_SESSION_TOKEN` from `.env`

**Solutions:**
```bash
# Check credentials
python3 scripts/check_aws_credentials.py

# For SSO: Refresh
python3 scripts/refresh_aws_credentials.py

# For IAM: Remove session token line from .env
```

### AccessDeniedException

**Error:** "User is not authorized to perform: bedrock:InvokeModel"

**Causes:**
1. IAM user lacks Bedrock permissions
2. Model access not enabled
3. Wrong region

**Solutions:**
1. Add `AmazonBedrockFullAccess` policy to IAM user
2. Enable model access in Bedrock console
3. Verify `AWS_REGION=us-east-1`

### ResourceNotFoundException

**Error:** "Could not resolve model"

**Causes:**
1. Model ID incorrect
2. Model not available in region
3. Model access not granted

**Solutions:**
1. Check model ID in `.env`
2. Verify us-east-1 has the models
3. Request model access in Bedrock console

### ThrottlingException

**Error:** "Rate exceeded"

**Causes:**
1. Too many requests too quickly
2. Exceeded account limits

**Solutions:**
1. Add retry logic (already implemented)
2. Request limit increase in AWS Console
3. Implement caching (see [Advanced Optimizations](07-ADVANCED-OPTIMIZATIONS.md))

---

## Cost Estimation

### Development/Testing (Low Volume)

**Assumptions:**
- 100 messages/day
- Average 50 tokens per message
- 10 searches/day

**Monthly costs:**
- Embeddings: ~$0.01
- Claude: ~$0.05
- **Total: < $0.10/month**

### Production (Medium Volume)

**Assumptions:**
- 10,000 messages/day
- 50 tokens per message
- 1,000 searches/day

**Monthly costs:**
- Embeddings: ~$0.75
- Claude: ~$7.50
- **Total: ~$8-10/month**

### High Volume

Costs scale linearly. Consider:
- Caching frequent queries
- Using cheaper models (Haiku)
- Batch processing
- Local embeddings for very high volume

---

## Security Best Practices

### IAM Users

1. **Rotate credentials** every 90 days
2. **Never commit** `.env` to git
3. **Use least privilege** permissions
4. **Enable MFA** on AWS account
5. **Monitor usage** in CloudTrail
6. **Delete unused** access keys

### SSO

1. **Set appropriate** session duration
2. **Use MFA** for SSO login
3. **Auto-refresh** credentials before expiry
4. **Centralize** access management
5. **Audit regularly** via SSO logs

### Credentials Storage

**DO:**
- Use `.env` file (git-ignored)
- Use AWS Secrets Manager (production)
- Use environment variables
- Encrypt at rest

**DON'T:**
- Hard-code in source
- Commit to version control
- Share in chat/email
- Store in plain text files in cloud storage

---

## Testing Bedrock Setup

### Test Script

```bash
# Test Titan embeddings
python3 scripts/test_embedding_model.py

# Test Claude model
python3 scripts/test_claude_arn.py

# Test both (comprehensive)
python3 scripts/check_aws_credentials.py
```

### Manual Test

```bash
# Start backend
python3 main.py

# Send message (triggers AI)
curl -X POST http://localhost:8182/conversation/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "conversation_id": "test",
    "type": "human",
    "text": "I love building recommendation systems with machine learning and collaborative filtering techniques"
  }'

# Check memories (should have AI summary and importance)
curl http://localhost:8182/memories/test | python3 -m json.tool
```

Look for:
- `summary`: AI-generated one-sentence summary
- `importance`: Score between 0.1 and 1.0
- Both indicate Bedrock is working

---

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Titan Embeddings Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
- [Claude Model Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

**Next:** [Troubleshooting Guide](05-TROUBLESHOOTING.md)
