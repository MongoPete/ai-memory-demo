# MongoDB + AI Workshop: Phase 1 - Critical Robustness

**Workshop Duration:** 4-6 hours  
**Level:** Intermediate  
**Prerequisites:** Python, MongoDB basics, AWS Bedrock familiarity

## 🎯 Learning Objectives

By completing this workshop, you will:

1. **Data Validation** - Implement schema validation in schema-less databases
2. **Index Health** - Monitor MongoDB Atlas Search indexes programmatically
3. **Pagination** - Handle large datasets with cursor-based pagination
4. **Rate Limiting** - Use MongoDB TTL indexes for rate limiting
5. **Embedding Validation** - Ensure vector search consistency
6. **Async Operations** - Implement non-blocking background tasks

## 📋 Prerequisites

### Required Knowledge
- Python 3.10+ (async/await, classes, decorators)
- MongoDB basics (queries, indexes, collections)
- REST APIs (FastAPI or Flask)
- Git/GitHub

### Required Setup
- MongoDB Atlas account (free M0 tier works)
- AWS account with Bedrock access
- Python 3.10+ installed
- Node.js 18+ (for testing frontend)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <repo-url>
cd ai-memory
git checkout workshop-phase1-materials
```

### 2. Install Dependencies

```bash
# Backend
pip3 install -r requirements.txt

# Frontend (optional)
cd figmaUI && npm install && cd ..
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your MongoDB URI and AWS credentials
```

### 4. Verify Setup

```bash
python3 scripts/validate_setup.py
```

## 📚 Workshop Structure

### Exercise 1: Data Validation (20-30 min)
**Problem:** Empty user_ids and malformed embeddings stored in MongoDB  
**Solution:** Application-level validation with clear error messages  
**MongoDB Concept:** Schema-less ≠ validation-less

📁 `_Workshop/exercises/01-data-validation/`

---

### Exercise 2: Index Health Monitoring (30-40 min)
**Problem:** Demo fails silently when Atlas Search indexes missing  
**Solution:** Programmatic index validation and health checks  
**MongoDB Concept:** Atlas Search indexes require manual creation

📁 `_Workshop/exercises/02-index-health/`

---

### Exercise 3: Pagination (40-50 min)
**Problem:** Loading all messages crashes with large conversations  
**Solution:** Cursor-based pagination with metadata  
**MongoDB Concept:** `.skip()` + `.limit()` vs cursor-based patterns

📁 `_Workshop/exercises/03-pagination/`

---

### Break (15 min) ☕

---

### Exercise 4: Rate Limiting (45-60 min)
**Problem:** No protection against API abuse  
**Solution:** MongoDB-based rate limiter with TTL indexes  
**MongoDB Concept:** TTL indexes for automatic data expiration

📁 `_Workshop/exercises/04-rate-limiting/`

---

### Exercise 5: Embedding Validation (30-40 min)
**Problem:** Wrong dimension embeddings crash vector search  
**Solution:** Validate embedding dimensions before storage  
**MongoDB Concept:** Vector search dimension requirements

📁 `_Workshop/exercises/05-embedding-validation/`

---

### Break (15 min) ☕

---

### Exercise 6: Async Background Tasks (40-50 min)
**Problem:** Memory pruning blocks API responses  
**Solution:** Non-blocking background tasks with asyncio  
**MongoDB Concept:** Async-safe MongoDB operations

📁 `_Workshop/exercises/06-async-pruning/`

---

### Discussion & Q&A (30 min)

---

## 🏃 Quick Start Guide

### Option A: Guided Workshop

Follow exercises in order:

```bash
cd _Workshop/exercises/01-data-validation
# Read README.md
# Implement solution
pytest test_validation.py -v
# Move to next exercise
```

### Option B: Self-Paced Learning

1. Read each exercise README
2. Try implementing yourself
3. Run tests to verify
4. Check hints if stuck
5. Compare with solution

## 📝 Running Tests

Each exercise has pre-written tests:

```bash
# Run specific exercise tests
cd _Workshop/exercises/01-data-validation
python -m pytest test_validation.py -v

# Run all tests
cd _Workshop
pytest exercises/ -v

# Run with coverage
pytest exercises/ -v --cov=database --cov=services
```

## 📖 Solutions

All solutions are in `_Workshop/solutions/`:

```
_Workshop/solutions/
├── database/
│   ├── models.py              # Exercise 1 & 5
│   └── index_validator.py      # Exercise 2
├── services/
│   ├── conversation_service.py # Exercise 3
│   ├── rate_limiter.py        # Exercise 4
│   └── memory_service.py      # Exercise 6
└── IMPLEMENTATION_NOTES.md
```

## 🎓 MongoDB Features Covered

| Feature | Exercise | Practical Use Case |
|---------|----------|-------------------|
| Schema Validation | 1 | Data consistency in schema-less DBs |
| Atlas Search Indexes | 2 | Production readiness checks |
| Cursor Pagination | 3 | Large dataset handling |
| TTL Indexes | 4 | Auto-expiring data (sessions, cache) |
| Vector Dimensions | 5 | AI/ML vector search |
| Async Operations | 6 | Non-blocking database ops |

## 🔧 Troubleshooting

### MongoDB Connection Issues
```bash
python3 scripts/check_aws_credentials.py
# Check MongoDB Atlas IP whitelist
# Verify connection string in .env
```

### Test Failures
- Read error messages carefully
- Check hints.md in exercise directory
- Compare with solution
- Ask instructor

### AWS Bedrock Issues
```bash
python3 scripts/test_bedrock_models.py
# Verify AWS credentials
# Check Bedrock model access
```

## 📚 Additional Resources

- [MongoDB Atlas Search Docs](https://www.mongodb.com/docs/atlas/atlas-search/)
- [Vector Search Guide](https://www.mongodb.com/docs/atlas/atlas-vector-search/)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## 💡 Tips for Success

1. **Read thoroughly** - Each README has important context
2. **Test frequently** - Run tests after each change
3. **Ask questions** - No question is too small
4. **Take breaks** - This is intensive material
5. **Compare solutions** - Learn from different approaches

## 🎯 What's Next?

After completing Phase 1:

- **Phase 2 Workshop** - Analytics, caching, change streams
- **Phase 3 Workshop** - Graph patterns, transactions, geospatial
- **Complete Demo** - See `phase1-complete` branch for full implementation

## 🤝 Contributing

Found an issue? Have a suggestion?

1. Create an issue on GitHub
2. Discuss with instructor
3. Submit a PR with improvements

## 📄 License

MIT License - See LICENSE file

---

**Ready to begin?** Start with Exercise 1: `cd _Workshop/exercises/01-data-validation`

**Need help?** Check the Instructor Guide: `_Workshop/INSTRUCTOR_GUIDE.md`

**Want context?** Read Implementation Notes: `_Workshop/solutions/IMPLEMENTATION_NOTES.md`
