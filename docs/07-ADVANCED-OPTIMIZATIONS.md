# Advanced Performance Optimizations

Production-ready optimizations for AI Memory Service.

## Overview

By default, search operations take **1-2 seconds** due to AWS Bedrock embedding generation. This is acceptable for demos but can be optimized for production use.

**Default flow:**
```
User types "machine learning"
  → Frontend sends search query
  → Backend calls AWS Bedrock (1000-1500ms)
  → Generate embedding vector
  → MongoDB vector search (50-200ms)
  → Return results
Total: ~1500-2000ms
```

This guide covers optimizations to reduce latency to **<100ms** for most queries.

---

## Optimization 1: Embedding Cache

**Impact:** ⚡⚡⚡⚡⚡ (1500ms → 50ms for repeated queries)  
**Complexity:** Low  
**Cost:** Free (uses RAM)

### How It Works

Cache generated embeddings in memory so identical queries don't call Bedrock again.

### Implementation

**File:** `services/bedrock_service.py`

```python
# Add at module level (already implemented in current code)
_embedding_cache = {}

def generate_embedding(text: str) -> list:
    """Generate embeddings with caching"""
    if not text.strip():
        return []
    
    # Normalize cache key
    cache_key = text.lower().strip()
    
    # Check cache first
    if cache_key in _embedding_cache:
        logger.debug(f"Cache hit for: {cache_key[:50]}")
        return _embedding_cache[cache_key]
    
    # Generate if not cached
    try:
        client = _get_bedrock_client()
        max_tokens = 8000
        tokens = text.split()
        text = " ".join(tokens[:max_tokens])
        payload = {"inputText": text}
        response = client.invoke_model(
            modelId=EMBEDDING_MODEL_ID,
            body=json.dumps(payload)
        )
        result = json.loads(response["body"].read())
        embedding = result["embedding"]
        
        # Store in cache
        _embedding_cache[cache_key] = embedding
        logger.debug(f"Cached new embedding for: {cache_key[:50]}")
        
        return embedding
    except Exception as e:
        logger.warning(f"Embedding generation failed: {e}")
        return []
```

### Cache Management

**Limit cache size** (prevent memory issues):

```python
MAX_CACHE_SIZE = 1000  # Adjust based on available RAM

def generate_embedding(text: str) -> list:
    cache_key = text.lower().strip()
    
    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]
    
    # Generate embedding...
    embedding = ...
    
    # Add to cache with size limit
    if len(_embedding_cache) >= MAX_CACHE_SIZE:
        # Remove oldest entry (FIFO)
        _embedding_cache.pop(next(iter(_embedding_cache)))
    
    _embedding_cache[cache_key] = embedding
    return embedding
```

**Clear cache periodically:**

```python
import time

_cache_timestamp = time.time()
CACHE_TTL = 3600  # 1 hour

def generate_embedding(text: str) -> list:
    global _cache_timestamp
    
    # Clear cache if expired
    if time.time() - _cache_timestamp > CACHE_TTL:
        _embedding_cache.clear()
        _cache_timestamp = time.time()
        logger.info("Embedding cache cleared (TTL expired)")
    
    # ... rest of function
```

### Results

- **First search:** 1500ms (Bedrock call)
- **Repeated searches:** 50ms (cache hit)
- **Memory usage:** ~6KB per cached embedding
- **1000 cached entries:** ~6MB RAM

**Ideal for:**
- Repeated user queries
- Common search terms
- Development/testing

---

## Optimization 2: Frontend Debouncing

**Impact:** ⚡⚡⚡ (Reduces unnecessary API calls)  
**Complexity:** Trivial  
**Cost:** Free

### How It Works

Wait for user to stop typing before triggering search. Prevents API call on every keystroke.

### Implementation

**File:** `figmaUI/app/components/unified-chat.tsx`

```typescript
// Current: 500ms debounce
const debouncedSearch = useDebounce(searchQuery, 500);

// Optimized: 800ms debounce
const debouncedSearch = useDebounce(searchQuery, 800);

// Aggressive: 1000ms debounce
const debouncedSearch = useDebounce(searchQuery, 1000);
```

### Tradeoffs

**Lower debounce (300ms):**
- More responsive
- More API calls
- Higher costs

**Higher debounce (1000ms):**
- Less responsive
- Fewer API calls
- Lower costs
- Better for slow typing

**Recommended:** 600-800ms for production

---

## Optimization 3: Use Cohere Embeddings

**Impact:** ⚡⚡⚡⚡ (1500ms → 500ms per search)  
**Complexity:** Low (config change + index update)  
**Cost:** Different pricing model

### How It Works

Cohere's embedding API is faster than AWS Titan. Similar quality, lower latency.

### Implementation

**Step 1: Enable Cohere in Bedrock**

1. AWS Console → Bedrock → Model access
2. Enable: `Cohere Embed English v3`
3. Wait for approval

**Step 2: Update config**

```bash
# .env
EMBEDDING_MODEL_ID=cohere.embed-english-v3
```

**Step 3: Update MongoDB indexes**

⚠️ Cohere uses **1024 dimensions** (Titan uses 1536)

```json
// MongoDB Atlas → Recreate vector indexes with:
{
  "fields": [
    {
      "type": "vector",
      "path": "embeddings",
      "numDimensions": 1024,  // Changed from 1536
      "similarity": "cosine"
    }
  ]
}
```

**Step 4: Re-embed existing data**

```python
# Migration script (run once)
from services.bedrock_service import generate_embedding
from database.mongodb import conversations, memory_nodes

# Re-embed conversations
for doc in conversations.find({}):
    new_embedding = generate_embedding(doc['text'])
    conversations.update_one(
        {"_id": doc["_id"]},
        {"$set": {"embeddings": new_embedding}}
    )

# Re-embed memories
for doc in memory_nodes.find({}):
    new_embedding = generate_embedding(doc['content'])
    memory_nodes.update_one(
        {"_id": doc["_id"]},
        {"$set": {"embeddings": new_embedding}}
    )
```

### Results

- **Latency:** 1500ms → 500ms per embedding
- **Quality:** Comparable to Titan
- **Cost:** Check Bedrock pricing for Cohere

---

## Optimization 4: Pre-generate Common Queries

**Impact:** ⚡⚡⚡ (Instant for common searches)  
**Complexity:** Medium  
**Cost:** Minimal

### How It Works

Pre-compute embeddings for common/predictable queries on startup.

### Implementation

**File:** `services/bedrock_service.py`

```python
# Pre-generate on server startup
COMMON_QUERIES = [
    "machine learning",
    "artificial intelligence",
    "recommendation system",
    "neural networks",
    "deep learning",
    "data science",
    "python programming",
    "software engineering",
    # Add your domain-specific terms
]

def preload_common_embeddings():
    """Pre-generate embeddings for common queries"""
    logger.info("Pre-loading common query embeddings...")
    for query in COMMON_QUERIES:
        generate_embedding(query)  # Will be cached
    logger.info(f"Pre-loaded {len(COMMON_QUERIES)} embeddings")

# In main.py startup:
@app.on_event("startup")
async def startup_event():
    initialize_mongodb()
    preload_common_embeddings()  # Add this
```

### Results

- Common queries: Instant (pre-cached)
- Startup time: +5-10 seconds
- Memory: ~6KB × number of queries

**Best for:**
- Applications with predictable query patterns
- Domain-specific searches
- FAQ-style queries

---

## Optimization 5: Local Embeddings

**Impact:** ⚡⚡⚡⚡⚡ (1500ms → 50ms for ALL searches)  
**Complexity:** High  
**Cost:** Free (uses CPU/GPU)

### How It Works

Run embedding model locally using `sentence-transformers` instead of calling AWS Bedrock.

### Implementation

**Step 1: Install dependencies**

```bash
pip install sentence-transformers
# For GPU support (optional):
# pip install torch torchvision torchaudio
```

**Step 2: Create local embedding service**

**File:** `services/local_embeddings.py`

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from utils.logger import logger

# Load model on startup (happens once)
_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading local embedding model...")
        # 384-dimension model (fast)
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        # Or for better quality (slower):
        # _model = SentenceTransformer('all-mpnet-base-v2')  # 768 dim
        logger.info("Local embedding model loaded")
    return _model

def generate_local_embedding(text: str) -> list:
    """Generate embedding locally without AWS"""
    if not text.strip():
        return []
    
    try:
        model = get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Local embedding failed: {e}")
        return []
```

**Step 3: Update bedrock_service to use local**

```python
# Add environment toggle
USE_LOCAL_EMBEDDINGS = os.getenv("USE_LOCAL_EMBEDDINGS", "false").lower() == "true"

def generate_embedding(text: str) -> list:
    """Generate embeddings (local or Bedrock)"""
    if USE_LOCAL_EMBEDDINGS:
        from services.local_embeddings import generate_local_embedding
        return generate_local_embedding(text)
    else:
        # Existing Bedrock logic...
        pass
```

**Step 4: Update configuration**

```bash
# .env
USE_LOCAL_EMBEDDINGS=true
```

**Step 5: Update MongoDB indexes**

⚠️ `all-MiniLM-L6-v2` uses **384 dimensions**

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embeddings",
      "numDimensions": 384,  // Changed from 1536
      "similarity": "cosine"
    }
  ]
}
```

### Model Options

| Model | Dimensions | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | High volume |
| all-mpnet-base-v2 | 768 | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Balanced |
| all-roberta-large-v1 | 1024 | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Quality |

### Results

- **Latency:** 1500ms → 50ms per embedding
- **Cost:** $0 (no AWS calls)
- **Quality:** Slightly lower than Titan
- **Hardware:** 2-4GB RAM, CPU sufficient (GPU optional)

### Tradeoffs

**Pros:**
- Zero cost
- Very fast
- No AWS dependency
- Predictable performance

**Cons:**
- Lower quality than Titan/Cohere
- Requires more server resources
- Model updates require code deploy
- Different dimensions (requires re-indexing)

---

## Optimization 6: Async/Background Processing

**Impact:** ⚡⚡ (User doesn't wait for AI processing)  
**Complexity:** Medium  
**Cost:** Free

### How It Works

Create memory nodes asynchronously so user doesn't wait for AI summarization.

### Implementation

**File:** `services/conversation_service.py`

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for background tasks
_executor = ThreadPoolExecutor(max_workers=4)

async def add_conversation_message(message_input):
    """Add message with async memory creation"""
    # Save message immediately
    new_message = Message(message_input)
    conversations.insert_one(new_message.to_dict())
    
    # Create memory in background (don't await)
    if message_input.type == "human" and len(message_input.text) > 30:
        asyncio.create_task(
            create_memory_async(message_input)
        )
    
    # Return immediately
    return {"message": "Message added successfully"}

async def create_memory_async(message_input):
    """Background memory creation"""
    try:
        memory_content = f"From conversation {message_input.conversation_id}: {message_input.text}"
        await remember_content(
            RememberRequest(
                user_id=message_input.user_id,
                content=memory_content
            )
        )
    except Exception as e:
        logger.error(f"Background memory creation failed: {e}")
```

### Results

- Message save: 50-100ms (immediate response)
- Memory creation: 2-3 seconds (background)
- User experience: Much faster

---

## Optimization 7: Redis Caching

**Impact:** ⚡⚡⚡⚡ (Persistent cache across restarts)  
**Complexity:** High  
**Cost:** Redis hosting ($10-50/month)

### How It Works

Use Redis for persistent embedding cache instead of in-memory dict.

### Implementation

```bash
pip install redis
```

```python
import redis
import json
import hashlib

# Connect to Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def generate_embedding(text: str) -> list:
    """Generate embedding with Redis cache"""
    if not text.strip():
        return []
    
    # Create cache key
    cache_key = f"embedding:{hashlib.md5(text.lower().encode()).hexdigest()}"
    
    # Check Redis cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Generate and cache
    embedding = _call_bedrock(text)
    redis_client.setex(
        cache_key,
        3600,  # 1 hour TTL
        json.dumps(embedding)
    )
    return embedding
```

---

## Performance Comparison

| Optimization | First Query | Repeated Query | Setup | Cost |
|-------------|-------------|----------------|-------|------|
| None (baseline) | 1500ms | 1500ms | Easy | Bedrock |
| In-memory cache | 1500ms | 50ms | Easy | Bedrock |
| Frontend debounce | 1500ms | 1500ms | Trivial | Bedrock |
| Cohere | 500ms | 500ms | Medium | Different |
| Pre-generated | 50ms* | 50ms* | Medium | Bedrock |
| Local embeddings | 50ms | 50ms | Hard | $0 |
| Redis cache | 1500ms | 50ms | Hard | Redis |

*For pre-generated queries only

---

## Recommended Combinations

### Development/Demo
```bash
✅ In-memory cache (already implemented)
✅ Frontend debounce: 500ms
```
**Result:** 1500ms first, 50ms repeated. Good enough.

### MVP/Small Production
```bash
✅ In-memory cache
✅ Frontend debounce: 800ms
✅ Pre-generated common queries
```
**Result:** <100ms for common, 1500ms for new.

### Medium Production
```bash
✅ Cohere embeddings (faster)
✅ In-memory cache with size limit
✅ Frontend debounce: 800ms
✅ Pre-generated common queries
```
**Result:** 500ms first, 50ms repeated. Better quality.

### High-Volume Production
```bash
✅ Local embeddings (sentence-transformers)
✅ Redis cache (persistent)
✅ Frontend debounce: 1000ms
✅ Async memory creation
```
**Result:** 50ms all queries. Zero Bedrock costs for embeddings.

---

## Implementation Priority

**Phase 1 (Immediate):**
1. ✅ In-memory cache (already done)
2. Increase frontend debounce to 800ms
3. Pre-generate 20-30 common queries

**Phase 2 (Before production):**
4. Switch to Cohere (if budget allows)
5. Add cache size limits
6. Implement async memory creation

**Phase 3 (High volume only):**
7. Migrate to local embeddings
8. Set up Redis for persistent cache
9. Add cache warming on startup

---

## Monitoring Performance

### Add Timing Logs

```python
import time

def generate_embedding(text: str) -> list:
    start = time.time()
    
    # ... embedding logic ...
    
    elapsed = time.time() - start
    logger.info(f"Embedding generated in {elapsed*1000:.0f}ms")
    
    return embedding
```

### Track Cache Hit Rate

```python
_cache_hits = 0
_cache_misses = 0

def generate_embedding(text: str) -> list:
    global _cache_hits, _cache_misses
    
    if cache_key in _embedding_cache:
        _cache_hits += 1
        hit_rate = _cache_hits / (_cache_hits + _cache_misses)
        logger.debug(f"Cache hit rate: {hit_rate:.2%}")
        return _embedding_cache[cache_key]
    
    _cache_misses += 1
    # ... generate ...
```

### Expose Metrics Endpoint

```python
@app.get("/metrics")
async def get_metrics():
    return {
        "cache_size": len(_embedding_cache),
        "cache_hits": _cache_hits,
        "cache_misses": _cache_misses,
        "hit_rate": _cache_hits / max(_cache_hits + _cache_misses, 1)
    }
```

---

## Cost Analysis

### Baseline (No Optimization)

**Assumptions:**
- 1000 searches/day
- Each search = 1 embedding + 1 Claude call (summary)

**Monthly costs:**
- Embeddings: 1000 × 30 × $0.0001 = **$3**
- Claude: 1000 × 30 × $0.001 = **$30**
- **Total: ~$33/month**

### With Cache (80% hit rate)

- Embeddings: 200 × 30 × $0.0001 = **$0.60**
- Claude: 1000 × 30 × $0.001 = **$30**
- **Total: ~$31/month** (small savings)

### With Local Embeddings

- Embeddings: **$0**
- Claude: 1000 × 30 × $0.001 = **$30**
- **Total: ~$30/month** (10% savings)

### High Volume (10,000 searches/day)

**Bedrock:**
- **$330/month**

**Local:**
- **$300/month** (only Claude)
- **Savings: $30/month**

At scale, local embeddings save significantly.

---

## Next Steps

1. Choose optimization level based on:
   - Traffic volume
   - Budget
   - Quality requirements
   - Infrastructure availability

2. Test in development first

3. Monitor metrics after deployment

4. Iterate based on real usage

---

**Quick wins:** Already implemented cache + increase debounce

**For production:** Add Cohere or local embeddings

**For scale:** Full local stack + Redis
