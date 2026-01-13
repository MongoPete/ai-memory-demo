# Deployment Guide

Production deployment guide for AI Memory Service.

## Overview

This application consists of two parts:
- **Backend:** Python FastAPI application
- **Frontend:** React SPA (Single Page Application)

Both can be deployed separately to different platforms.

---

## Deployment Architecture

### Recommended Setup

```
User Browser
     ↓
Vercel (Frontend - Static React app)
     ↓ API calls
AWS ECS/Lambda (Backend - FastAPI)
     ↓
MongoDB Atlas (Database)
     ↓
AWS Bedrock (AI Services)
```

**Benefits:**
- CDN for frontend (fast global access)
- Scalable backend
- Managed database
- Serverless AI

---

## Frontend Deployment (Vercel)

### Prerequisites
- GitHub/GitLab account with code pushed
- Vercel account (free tier sufficient)

### Option 1: Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd figmaUI

# Deploy
vercel deploy --prod

# Follow prompts:
# - Link to existing project or create new
# - Set root directory: ./figmaUI
# - Build command: npm run build
# - Output directory: dist
```

### Option 2: Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your repository
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `figmaUI`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add environment variable:
   - `VITE_API_BASE_URL` = your backend URL
5. Deploy

### Environment Variables

```bash
# Production
VITE_API_BASE_URL=https://api.yourdomain.com

# Staging
VITE_API_BASE_URL=https://api-staging.yourdomain.com
```

### Custom Domain

1. Vercel Dashboard → Your Project → Settings → Domains
2. Add domain: `app.yourdomain.com`
3. Configure DNS (Vercel provides instructions)
4. SSL certificate auto-provisioned

---

## Backend Deployment Options

### Option 1: AWS ECS (Elastic Container Service)

**Best for:** Production workloads, auto-scaling

#### Step 1: Create Docker Image

```bash
# Build
docker build -t ai-memory-service:latest .

# Test locally
docker run -p 8182:8182 --env-file .env ai-memory-service:latest
```

#### Step 2: Push to ECR (Elastic Container Registry)

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name ai-memory-service --region us-east-1

# Tag image
docker tag ai-memory-service:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-memory-service:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-memory-service:latest
```

#### Step 3: Create ECS Task Definition

```json
{
  "family": "ai-memory-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "ai-memory",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-memory-service:latest",
      "portMappings": [
        {
          "containerPort": 8182,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "SERVICE_HOST", "value": "0.0.0.0"},
        {"name": "SERVICE_PORT", "value": "8182"}
      ],
      "secrets": [
        {
          "name": "MONGODB_URI",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:...:secret:mongodb-uri"
        },
        {
          "name": "AWS_ACCESS_KEY_ID",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:...:secret:bedrock-key-id"
        },
        {
          "name": "AWS_SECRET_ACCESS_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:...:secret:bedrock-secret"
        }
      ]
    }
  ]
}
```

#### Step 4: Create ECS Service

```bash
aws ecs create-service \
  --cluster default \
  --service-name ai-memory-service \
  --task-definition ai-memory-service \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### Step 5: Configure Load Balancer

1. Create Application Load Balancer
2. Target group: Port 8182
3. Health check: `/health`
4. Add ECS service to target group

---

### Option 2: AWS Lambda (Serverless)

**Best for:** Low traffic, cost optimization, sporadic usage

#### Using Mangum (ASGI adapter)

```python
# lambda_handler.py
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="off")
```

#### Deploy with AWS SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  AIMemoryFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_handler.handler
      Runtime: python3.10
      MemorySize: 512
      Timeout: 30
      Environment:
        Variables:
          MONGODB_URI: !Ref MongoDBURI
          AWS_REGION: us-east-1
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

```bash
# Build and deploy
sam build
sam deploy --guided
```

**Limitations:**
- 15-minute timeout (may not suit all workloads)
- Cold starts (1-3 seconds)
- Stateless (no in-memory cache between invocations)

---

### Option 3: Traditional VPS (DigitalOcean, Linode, etc.)

**Best for:** Simple deployments, full control

#### Setup

```bash
# SSH to server
ssh user@your-server.com

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx

# Clone repository
git clone <your-repo>
cd ai-memory

# Install packages
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add credentials

# Run with supervisor
sudo apt install supervisor

# Create supervisor config: /etc/supervisor/conf.d/ai-memory.conf
[program:ai-memory]
directory=/home/user/ai-memory
command=/usr/bin/python3 main.py
user=user
autostart=true
autorestart=true
stderr_logfile=/var/log/ai-memory.err.log
stdout_logfile=/var/log/ai-memory.out.log

# Start
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-memory
```

#### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/ai-memory
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8182;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-memory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

---

## Environment Configuration

### Production Environment Variables

```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://prod_user:strong_password@cluster.mongodb.net/

# AWS Bedrock (use IAM role if on AWS)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Models
LLM_MODEL_ID=arn:aws:bedrock:us-east-1:...:inference-profile/...
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# Service
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8182
DEBUG=false

# CORS (add your frontend domain)
CORS_ORIGINS=https://app.yourdomain.com,https://www.yourdomain.com
```

### Secrets Management

**AWS Secrets Manager (Recommended for AWS deployments):**

```bash
# Store MongoDB URI
aws secretsmanager create-secret \
  --name ai-memory/mongodb-uri \
  --secret-string "mongodb+srv://..."

# Store AWS credentials
aws secretsmanager create-secret \
  --name ai-memory/bedrock-credentials \
  --secret-string '{"access_key":"AKIA...","secret_key":"..."}'

# Retrieve in code
import boto3

client = boto3.client('secretsmanager')
mongodb_uri = client.get_secret_value(SecretId='ai-memory/mongodb-uri')['SecretString']
```

**Environment Variables (Simpler for VPS):**

```bash
# Use .env file (never commit!)
# Or set in supervisor/systemd config
```

---

## Database Configuration

### MongoDB Atlas Production Setup

1. **Upgrade Tier:**
   - Free M0: Development only
   - M2/M5: Small production
   - M10+: Production with backups

2. **Enable Backups:**
   - Atlas → Backup → Enable
   - Continuous backups (M10+)
   - Snapshot schedule

3. **Network Access:**
   - Remove 0.0.0.0/0 (allow all)
   - Add specific IPs/CIDR blocks
   - Use VPC peering for AWS ECS

4. **Create Indexes** (if not done):
   - See [MongoDB Atlas Guide](03-MONGODB-ATLAS.md)

---

## Monitoring & Logging

### Backend Logging

**Structured logging:**

```python
# utils/logger.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        })
```

**CloudWatch (for AWS):**

```python
import watchtower

logger.addHandler(watchtower.CloudWatchLogHandler())
```

### Health Checks

**Endpoint:** `/health`

**Monitor:**
- Response time
- MongoDB status
- Bedrock availability
- Memory usage

**Uptime monitoring tools:**
- UptimeRobot (free)
- Pingdom
- AWS CloudWatch Alarms

---

## Performance Optimization

### Production Optimizations

1. **Enable caching** (already implemented)
2. **Use CDN** for frontend (Vercel includes)
3. **Connection pooling** for MongoDB
4. **Increase debounce** to 800ms
5. **Consider Cohere** for faster embeddings

See [Advanced Optimizations](07-ADVANCED-OPTIMIZATIONS.md)

### Scaling

**Horizontal scaling (ECS):**
```bash
# Increase desired count
aws ecs update-service \
  --cluster default \
  --service ai-memory-service \
  --desired-count 3
```

**Auto-scaling (ECS):**
```bash
# Create scaling policy based on CPU
aws application-autoscaling put-scaling-policy \
  --policy-name cpu-scaling \
  --service-namespace ecs \
  --resource-id service/default/ai-memory-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

---

## Security Checklist

- [ ] Remove DEBUG=true in production
- [ ] Use HTTPS only (SSL certificates)
- [ ] Restrict CORS to your domain
- [ ] MongoDB: IP whitelist (no 0.0.0.0/0)
- [ ] AWS: IAM roles instead of keys (if possible)
- [ ] Secrets in Secrets Manager (not .env)
- [ ] Enable MongoDB Atlas encryption
- [ ] Regular security updates (dependencies)
- [ ] Rate limiting on API endpoints
- [ ] Input validation (already implemented)

---

## CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: 18
      - run: cd figmaUI && npm install && npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: docker build -t ai-memory .
      - run: docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-memory:latest
      - run: aws ecs update-service --cluster default --service ai-memory --force-new-deployment
```

---

## Rollback Strategy

### Frontend (Vercel)
- Vercel keeps all deployments
- Dashboard → Deployments → Promote previous version

### Backend (ECS)
```bash
# Revert to previous task definition
aws ecs update-service \
  --cluster default \
  --service ai-memory-service \
  --task-definition ai-memory-service:2  # Previous revision
```

### Database
- MongoDB Atlas: Restore from snapshot
- Backup before schema changes

---

## Cost Estimation (Production)

### Medium Traffic (10,000 req/day)

**Vercel:** Free (hobby tier sufficient)

**AWS ECS:**
- Fargate: $15-30/month (1 task, 0.25 vCPU, 0.5GB RAM)
- Load Balancer: $16/month
- **Subtotal: ~$30-45/month**

**MongoDB Atlas:**
- M2 Shared: $9/month
- M10 Dedicated: $57/month
- **Recommended: M10 for backups**

**AWS Bedrock:**
- Embeddings: $3/month
- Claude: $20/month
- **Subtotal: ~$25/month**

**Total: ~$90-125/month** for production setup

---

## Post-Deployment Checklist

- [ ] Health endpoint returns 200
- [ ] Frontend loads and connects to backend
- [ ] CORS working (no browser errors)
- [ ] MongoDB connection active
- [ ] AWS Bedrock accessible
- [ ] Search indexes active
- [ ] Test all features:
  - [ ] Send message
  - [ ] Search conversations
  - [ ] Create memory
  - [ ] View memories
- [ ] SSL certificate active
- [ ] Monitoring alerts configured
- [ ] Backup schedule active
- [ ] Documentation updated with URLs

---

## Support

**Issues after deployment?**
1. Check backend logs (CloudWatch, server logs)
2. Test `/health` endpoint
3. Verify environment variables
4. Check security groups / firewall
5. Review [Troubleshooting Guide](05-TROUBLESHOOTING.md)

---

**Ready to deploy?** Start with Vercel for frontend (5 minutes) and VPS for backend (simplest) before moving to AWS ECS.
