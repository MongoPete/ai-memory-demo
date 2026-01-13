# Instructor Guide: Phase 1 Workshop

**Workshop Name:** MongoDB + AI: Critical Robustness Patterns  
**Duration:** 4-6 hours  
**Target Audience:** Intermediate developers

## 🎯 Workshop Goals

1. Teach MongoDB best practices for AI applications
2. Demonstrate production-ready patterns
3. Show how MongoDB fits into AI ecosystem
4. Hands-on learning with real code

## 📅 Recommended Schedule

### Morning Session (2.5-3 hours)

**09:00-09:15** - Introduction & Setup (15 min)
- Welcome & introductions
- Overview of workshop
- Verify everyone's setup

**09:15-09:45** - Exercise 1: Data Validation (30 min)
- Emphasize schema-less ≠ validation-less
- Show real-world consequences of missing validation
- Discuss defensive programming

**09:45-10:30** - Exercise 2: Index Health (45 min)
- Explain Atlas Search vs regular indexes
- Discuss production readiness
- Show MongoDB Atlas UI

**10:30-10:45** - Break ☕

**10:45-11:30** - Exercise 3: Pagination (45 min)
- Discuss performance implications
- Compare pagination strategies
- Show real performance data

### Afternoon Session (2.5-3 hours)

**13:00-14:00** - Exercise 4: Rate Limiting (60 min)
- Explain TTL indexes deeply
- Discuss alternatives (Redis vs MongoDB)
- Show time-series patterns

**14:00-14:15** - Break ☕

**14:15-14:45** - Exercise 5: Embedding Validation (30 min)
- Explain vector search requirements
- Discuss dimension matching
- Show failure scenarios

**14:45-15:30** - Exercise 6: Async Operations (45 min)
- Discuss async/await patterns
- Show blocking vs non-blocking
- MongoDB async safety

**15:30-16:00** - Q&A & Wrap-up (30 min)
- Review key concepts
- Discuss Phase 2 topics
- Collect feedback

## 🎓 Teaching Notes

### Exercise 1: Data Validation

**Key Points:**
- MongoDB won't enforce schema, your app must
- Fail fast with clear errors
- Validation is documentation

**Common Mistakes:**
- Validating after assignment (wrong order)
- Not stripping whitespace
- Unclear error messages

**Discussion Topics:**
- When to use MongoDB schema validation vs app validation
- Pydantic for API validation vs database validation
- Performance impact of validation

**Demo Opportunity:**
Show what happens when bad data gets into MongoDB:
```python
# Insert bad data directly
db.conversations.insert_one({"user_id": "", "text": ""})
# Now try to search - what breaks?
```

---

### Exercise 2: Index Health Monitoring

**Key Points:**
- Atlas Search indexes are NOT automatic
- Production readiness requires index checks
- Clear error messages save debugging time

**Common Mistakes:**
- Using `.listIndexes()` instead of `.list_search_indexes()`
- Not handling exceptions
- Forgetting to check both collections

**Discussion Topics:**
- Infrastructure as Code for indexes (Terraform)
- Atlas Admin API for automation
- Monitoring strategies

**Live Demo:**
- Show MongoDB Atlas UI
- Create an index together
- Show how long it takes (educate on patience)

**Pro Tip:**
Have backup screenshots of Atlas UI in case of connectivity issues.

---

### Exercise 3: Pagination

**Key Points:**
- `.skip()` is slow for large offsets
- Cursor-based pagination is faster
- Always include pagination metadata

**Common Mistakes:**
- Forgetting to count total documents
- Not handling empty results
- Incorrect has_next calculation

**Discussion Topics:**
- Performance: skip(10000) vs cursor-based
- UI/UX considerations
- Infinite scroll vs page numbers

**Benchmark Demo:**
```python
# Show performance difference
import time

# Method 1: skip/limit
start = time.time()
list(collection.find().skip(10000).limit(50))
print(f"Skip: {time.time() - start}")

# Method 2: cursor-based
start = time.time()
list(collection.find({"_id": {"$gt": last_id}}).limit(50))
print(f"Cursor: {time.time() - start}")
```

---

### Exercise 4: Rate Limiting

**Key Points:**
- TTL indexes for auto-expiration
- MongoDB as rate limiting store
- Atomic operations important

**Common Mistakes:**
- Not creating TTL index
- Wrong expireAfterSeconds value
- Not handling clock skew

**Discussion Topics:**
- MongoDB vs Redis for rate limiting
- Distributed rate limiting challenges
- Sliding window vs fixed window

**Advanced Topic:**
Token bucket algorithm with MongoDB:
```python
# Show how to implement token bucket
# Discuss trade-offs
```

**Warning:**
TTL index deletion is not instant (runs every 60 seconds). Set expectations!

---

### Exercise 5: Embedding Validation

**Key Points:**
- Vector dimensions must match index
- Silent failures are dangerous
- Validate early in pipeline

**Common Mistakes:**
- Not handling None/empty embeddings
- Wrong dimension count
- Not configurable for different models

**Discussion Topics:**
- Different embedding models (Titan, Cohere, OpenAI)
- Dimension reduction techniques
- Vector quantization

**Demo:**
Show what happens with wrong dimensions:
```python
# Create 768-dim embedding (BERT)
# Try to insert into 1536-dim index
# Show the error
```

---

### Exercise 6: Async Background Tasks

**Key Points:**
- Blocking operations hurt UX
- Python asyncio for I/O-bound tasks
- MongoDB is async-safe

**Common Mistakes:**
- Using threads for CPU-bound tasks (use processes)
- Not handling task failures
- Memory leaks in long-running tasks

**Discussion Topics:**
- asyncio vs threading vs multiprocessing
- Celery for production
- Task queues (RabbitMQ, Redis)

**Advanced Demo:**
```python
import asyncio
import time

# Show blocking version
def blocking_prune():
    time.sleep(2)  # Simulates database work
    
# Show async version
async def async_prune():
    await asyncio.sleep(2)
    
# Compare user experience
```

---

## 💬 Discussion Prompts

Throughout the workshop, use these to spark conversation:

1. **"Have you experienced this issue in production?"**
   - Gets people sharing war stories
   - Makes concepts real

2. **"How would you handle this in your stack?"**
   - Encourages knowledge sharing
   - Shows multiple approaches

3. **"What could go wrong here?"**
   - Develops defensive thinking
   - Uncovers edge cases

4. **"How would this scale to 1M users?"**
   - Thinking about production
   - Performance considerations

## 🐛 Common Issues & Solutions

### Issue: Tests fail with import errors
**Solution:** Ensure participants run tests from correct directory
```bash
cd _Workshop/exercises/01-data-validation
python -m pytest test_validation.py -v
```

### Issue: MongoDB connection fails
**Solution:** Check Atlas IP whitelist, verify connection string
```bash
python3 scripts/validate_setup.py
```

### Issue: AWS Bedrock unavailable
**Solution:** Check credentials, verify model access
```bash
python3 scripts/check_aws_credentials.py
```

### Issue: Participants moving too fast
**Solution:** Encourage reading, not just coding
- "Let's discuss the problem first"
- "What's the MongoDB concept here?"

### Issue: Participants stuck
**Solution:** Progressive hints
1. Point to hints.md
2. Discuss approach (not code)
3. Show solution section (last resort)

## ⏱️ Time Management

**Running Behind?**
- Skip Exercise 5 (easiest to skip)
- Shorten Q&A
- Do Exercise 6 as demo instead of hands-on

**Running Ahead?**
- Deeper discussion on each topic
- Show production examples
- Discuss Phase 2 topics early

**Individual Pace Variance?**
- Fast finishers: Ask them to help others
- Struggling: Pair them up
- Everyone: Solutions available anytime

## 📊 Assessment

**Informal Assessment:**
- Can they explain MongoDB concepts?
- Do solutions work correctly?
- Are they asking good questions?

**End of Workshop:**
- Quick survey (Google Form)
- What was most valuable?
- What needs improvement?
- Would they recommend to others?

## 🎁 Bonus Content

If time permits or for advanced participants:

1. **MongoDB Transactions** - When and why
2. **Change Streams** - Real-time updates
3. **Aggregation Pipelines** - Complex queries
4. **Sharding** - Horizontal scaling
5. **Atlas Admin API** - Automation

## 📝 Instructor Checklist

**Before Workshop:**
- [ ] Test all exercises yourself
- [ ] Verify MongoDB Atlas access
- [ ] Check AWS Bedrock credentials
- [ ] Prepare backup demos (screenshots, videos)
- [ ] Review latest MongoDB docs
- [ ] Set up Zoom/screen sharing
- [ ] Prepare feedback form

**During Workshop:**
- [ ] Start with energy and enthusiasm
- [ ] Check understanding frequently
- [ ] Encourage questions
- [ ] Take breaks on time
- [ ] Monitor chat/questions
- [ ] Adjust pace as needed

**After Workshop:**
- [ ] Collect feedback
- [ ] Share additional resources
- [ ] Answer follow-up questions
- [ ] Update materials based on feedback

## 📚 Resources for Instructors

- [MongoDB University](https://university.mongodb.com/)
- [Atlas Search Documentation](https://docs.mongodb.com/atlas/atlas-search/)
- [Python asyncio Guide](https://docs.python.org/3/library/asyncio.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)

---

**Remember:** The goal is learning, not just completing exercises. Encourage understanding over speed!

**Good luck! 🚀**
