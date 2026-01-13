# AI Memory Service

MongoDB Atlas Vector Search + AWS Bedrock Demo

[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)](https://www.mongodb.com/atlas)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)](https://fastapi.tiangolo.com/)

A production-ready demonstration of semantic search and AI memory management using MongoDB's vector search capabilities with AWS Bedrock AI services.

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Clone and install
git clone <your-repo-url>
cd ai-memory
pip3 install -r requirements.txt
cd figmaUI && npm install && cd ..

# 2. Configure
cp .env.example .env
# Edit .env with your MongoDB URI and AWS credentials

# 3. Start
./scripts/start_demo.sh

# 4. Open
# http://localhost:5173
```

**[→ Detailed Setup Guide](docs/02-SETUP-GUIDE.md)**

---

## 🎯 What This Demonstrates

### MongoDB Atlas Features
- ✅ **Vector Search** - 1536-dimension semantic search with Titan embeddings
- ✅ **Hybrid Search** - Combined full-text and vector search
- ✅ **Real-time Indexing** - Instant search across conversations
- ✅ **Cross-collection Queries** - Search across users and conversations

### AWS Bedrock Features
- ✅ **Titan Embeddings** - High-quality vector generation
- ✅ **Claude AI** - Intelligent importance assessment
- ✅ **AI Summarization** - Context-aware summaries
- ✅ **Dynamic Memory** - Reinforcement and decay algorithms

### Application Features
- ✅ **Single-user Chat** - Real-time conversation with semantic search
- ✅ **Multi-user Demo** - Split-screen with global search
- ✅ **Memory Dashboard** - AI-generated memory visualization
- ✅ **Real-time Vectorization** - Watch embeddings being created

---

## 🎓 Workshop & Advanced Features

### 📚 Workshop Materials (Educational Branch)

**Branch:** `workshop-phase1-materials`

A comprehensive hands-on workshop teaching MongoDB best practices for AI applications:
- **6 progressive exercises** (4-6 hours total)
- Test-driven development approach
- Clear problem statements & solutions
- Instructor guide included

**Topics Covered:**
1. Data Validation & Error Handling
2. Index Health Monitoring
3. Pagination for Scale
4. Rate Limiting with MongoDB
5. Embedding Dimension Validation
6. Async Background Tasks

```bash
git checkout workshop-phase1-materials
cd _Workshop
# See README.md for instructions
```

[**→ View Workshop Materials**](../../tree/workshop-phase1-materials/_Workshop)

---

### 🚀 Complete Demo (Production-Ready Branch)

**Branch:** `phase1-complete`

Fully integrated Phase 1 improvements with admin dashboard for demonstrations:
- ✅ **All validations** integrated
- ✅ **Pagination** on all endpoints
- ✅ **Rate limiting** enabled
- ✅ **Index monitoring** built-in
- ✅ **Admin Dashboard** for real-time monitoring

**Admin Dashboard Features:**
- System health overview
- Rate limiting visualization
- Search analytics & metrics
- Background task monitoring
- Index health indicators

```bash
git checkout phase1-complete
# Production-ready demo with monitoring
```

[**→ View Complete Demo**](../../tree/phase1-complete)  
[**→ Phase 1 Documentation**](docs/09-PHASE1-FEATURES.md)

---

## 🏗 Architecture

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│   React Frontend (Vite + Tailwind)  │
│   • Unified Chat Interface          │
│   • Split-screen Demo Mode          │
│   • Memory Dashboard                │
└──────┬──────────────────────────────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────┐
│   FastAPI Backend (Python)          │
│   • /conversation/ (add messages)   │
│   • /retrieve_memory/ (search)      │
│   • /memories/{user_id} (list)      │
└──────┬─────────────┬────────────────┘
       │             │
       ▼             ▼
┌──────────────┐  ┌──────────────────┐
│  MongoDB     │  │  AWS Bedrock     │
│  Atlas       │  │  • Titan Embed   │
│  • Vector DB │  │  • Claude AI     │
│  • Search    │  │                  │
└──────────────┘  └──────────────────┘
```

**Tech Stack:**
- **Backend:** Python 3.10+, FastAPI, pymongo
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Database:** MongoDB Atlas (Vector Search + Full-text Search)
- **AI:** AWS Bedrock (Titan Embeddings + Claude)
- **Deployment:** Docker, AWS (backend) | Vercel (frontend)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Quick Start](docs/01-QUICKSTART.md)** | Get running in 5-10 minutes |
| **[Setup Guide](docs/02-SETUP-GUIDE.md)** | Complete installation instructions |
| **[MongoDB Atlas](docs/03-MONGODB-ATLAS.md)** | Vector search index setup |
| **[AWS Bedrock](docs/04-AWS-BEDROCK.md)** | Model access and credentials |
| **[Troubleshooting](docs/05-TROUBLESHOOTING.md)** | Common issues and solutions |
| **[Deployment](docs/06-DEPLOYMENT.md)** | Production deployment guide |
| **[Advanced Optimizations](docs/07-ADVANCED-OPTIMIZATIONS.md)** | Performance tuning |
| **[Tuning Semantic Search](docs/08-TUNING-SEMANTIC-SEARCH.md)** | Adjust search relevance |

---

## 🎮 Demo Features

### 1. Unified Chat View
**Purpose:** Single-user conversation with real-time semantic search

**Try it:**
```
User ID: alice
Conversation: demo_test
Message: "I'm building a recommendation system using collaborative filtering and neural networks"
```

Then search for: `machine learning` (note: different words, semantic match!)

**Watch:**
- Real-time vectorization indicator
- Embedding generation
- Semantic search results (finds related concepts, not just keywords)

### 2. Multi-User Demo Mode
**Purpose:** Showcase cross-user search and multi-conversation handling

**Try it:**
- Send messages as Alice, Bob, and Carol
- Each user has their own conversation
- Use global search to find across all users

**Demonstrates:**
- User isolation
- Cross-user search
- Conversation threading
- Scalability

### 3. Memory Dashboard
**Purpose:** Visualize AI-generated memories with importance scoring

**Features:**
- AI-generated summaries (Claude)
- Importance scores (0-1 scale)
- Access count tracking
- Memory reinforcement visualization

---

## 🔧 Configuration

### Required Environment Variables

   ```bash
# MongoDB Atlas (Required)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# AWS Bedrock (Required)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Models (Optional - has defaults)
LLM_MODEL_ID=arn:aws:bedrock:us-east-1:...:inference-profile/...
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
```

**[→ Full Configuration Guide](docs/02-SETUP-GUIDE.md#application-configuration)**

### MongoDB Atlas Setup

**Required:** 3 search indexes

1. **`conversations_vector_search_index`** - Vector search (1536 dim, cosine)
2. **`conversations_fulltext_search_index`** - Full-text search
3. **`memory_nodes_vector_search_index`** - Memory vector search

**[→ Index Creation Guide](docs/03-MONGODB-ATLAS.md#creating-search-indexes)**

---

## 🧪 Testing

### Verify Setup
```bash
# Check environment
python3 -c "import config; print('✅ Config OK')"

# Test AWS credentials
python3 scripts/check_aws_credentials.py

# Comprehensive validation
python3 scripts/validate_setup.py
```

### Test Backend
```bash
# Start backend
python3 main.py

# Health check
curl http://localhost:8182/health | python3 -m json.tool

# Send test message
curl -X POST http://localhost:8182/conversation/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "conversation_id": "test",
      "type": "human",
    "text": "Testing the AI memory system with machine learning"
  }'
```

### Test Frontend
```bash
cd figmaUI
npm run dev
# Open http://localhost:5173
```

**[→ Complete Testing Guide](docs/01-QUICKSTART.md#5-open-and-test)**

---

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd figmaUI
vercel deploy
```

### Backend (AWS/Docker)
```bash
docker build -t ai-memory-service .
docker run -p 8182:8182 --env-file .env ai-memory-service
```

**[→ Production Deployment Guide](docs/06-DEPLOYMENT.md)**

---

## 💡 How It Works

### Memory Creation Flow

```
1. User sends message → Backend
2. Message saved to MongoDB
3. AWS Bedrock generates embedding (1536-dim vector)
4. For significant messages (>30 chars):
   a. Claude assesses importance (0-1 scale)
   b. Claude generates summary
   c. Memory node created
5. MongoDB indexes for search
```

### Search Flow

```
1. User types search query
2. Frontend debounces (500ms)
3. Backend generates query embedding (Titan)
4. MongoDB hybrid search:
   a. Vector search (semantic)
   b. Full-text search (keywords)
   c. Combine results (weighted)
5. Filter by similarity threshold (>0.70)
6. Return top results
```

### Memory Management

**Reinforcement:** Similar memories (0.85+ similarity) get importance boost
**Merging:** Related memories (0.70-0.85) combined into single node
**Decay:** Unused memories lose importance over time
**Pruning:** Maximum 5 memories per user (lowest importance removed)

---

## 📊 Performance

### Default Performance
- **Message save:** 100-200ms
- **Search (first time):** 1500-2000ms (Bedrock call)
- **Search (cached):** 50-100ms
- **Memory creation:** 2-3s (async, doesn't block)

### Optimizations Available
- **Embedding cache:** Already implemented (50ms repeated searches)
- **Cohere embeddings:** 2-3x faster than Titan
- **Local embeddings:** Zero cost, 50ms all searches
- **Redis cache:** Persistent across restarts

**[→ Performance Optimization Guide](docs/07-ADVANCED-OPTIMIZATIONS.md)**

---

## 🛠 Development

### Project Structure
```
ai-memory/
├── main.py                 # FastAPI application
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
│
├── services/             # Business logic
│   ├── bedrock_service.py    # AWS Bedrock integration
│   ├── conversation_service.py # Chat & search
│   └── memory_service.py     # Memory management
│
├── database/             # Data layer
│   ├── mongodb.py           # MongoDB client
│   └── models.py            # Data models
│
├── models/               # API models
│   └── pydantic_models.py   # Request/response schemas
│
├── utils/                # Utilities
│   ├── logger.py
│   ├── env_validator.py
│   └── helpers.py
│
├── scripts/              # Helper scripts
│   ├── check_aws_credentials.py
│   ├── refresh_aws_credentials.py
│   ├── validate_setup.py
│   └── start_demo.sh
│
├── figmaUI/              # React frontend
│   ├── app/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── unified-chat.tsx
│   │   │   ├── split-screen-demo.tsx
│   │   │   ├── memory-dashboard.tsx
│   │   │   └── ui/         # shadcn/ui components
│   │   └── config.ts
│   ├── package.json
│   └── vite.config.ts
│
└── docs/                 # Documentation
    ├── 01-QUICKSTART.md
    ├── 02-SETUP-GUIDE.md
    ├── 03-MONGODB-ATLAS.md
    ├── 04-AWS-BEDROCK.md
    ├── 05-TROUBLESHOOTING.md
    ├── 06-DEPLOYMENT.md
    └── 07-ADVANCED-OPTIMIZATIONS.md
```

### Local Development
```bash
# Backend with auto-reload
DEBUG=true python3 main.py

# Frontend with HMR
cd figmaUI && npm run dev

# Run tests
python3 -m pytest tests/

# Format code
black . && isort .
```

---

## 🔐 Security

- ✅ Environment variables (never commit `.env`)
- ✅ CORS configuration
- ✅ IAM role-based access (AWS)
- ✅ IP whitelisting (MongoDB Atlas)
- ✅ Input validation (Pydantic)
- ✅ Error handling without exposing internals

**[→ Security Best Practices](docs/04-AWS-BEDROCK.md#security-best-practices)**

---

## 💰 Cost Estimate

### Development/Demo (Low Volume)
- MongoDB Atlas: **Free** (M0 tier)
- AWS Bedrock: **< $1/month** (100 messages/day)
- **Total: ~$0-1/month**

### Production (Medium Volume)
- MongoDB Atlas: **$9/month** (M2 tier)
- AWS Bedrock: **$10-20/month** (10,000 messages/day)
- **Total: ~$20-30/month**

**Notes:**
- Free tier sufficient for demos
- Costs scale linearly with usage
- Optimizations can reduce by 50-90%

**[→ Detailed Cost Analysis](docs/07-ADVANCED-OPTIMIZATIONS.md#cost-analysis)**

---

## 🤝 Contributing

Contributions welcome! This is a demonstration project showing MongoDB Atlas and AWS Bedrock integration.

**Ideas for enhancement:**
- Add user authentication
- Implement conversation threads
- Add memory expiration
- Create admin dashboard
- Add more AI models
- Implement memory export
- Add usage analytics

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **MongoDB Atlas** - Vector search capabilities
- **AWS Bedrock** - Titan and Claude models
- **Anthropic** - Claude AI
- **FastAPI** - Modern Python web framework
- **React** + **Vite** - Frontend framework
- **shadcn/ui** - Beautiful UI components

---

## 📞 Support

**Issues?**
1. Check [Troubleshooting Guide](docs/05-TROUBLESHOOTING.md)
2. Review [Setup Guide](docs/02-SETUP-GUIDE.md)
3. Check backend logs for errors
4. Verify MongoDB Atlas and AWS Bedrock status

**Questions?**
- Review documentation in `docs/` folder
- Check inline code comments
- Examine configuration files

---

## ⚡ Quick Commands

```bash
# Full setup from scratch
./scripts/quick_setup.sh

# Start demo (both backend + frontend)
./scripts/start_demo.sh

# Validate configuration
python3 scripts/validate_setup.py

# Check AWS credentials
python3 scripts/check_aws_credentials.py

# Health check
curl http://localhost:8182/health

# Kill processes
pkill -9 -f "python3 main.py"
lsof -ti:8182 | xargs kill -9
```

---

**Ready to start?** → [Quick Start Guide](docs/01-QUICKSTART.md)

**Need help?** → [Troubleshooting](docs/05-TROUBLESHOOTING.md)

**Want to optimize?** → [Advanced Guide](docs/07-ADVANCED-OPTIMIZATIONS.md)
