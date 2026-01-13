# Tuning Semantic Search Thresholds

A practical guide to understanding and adjusting semantic search behavior for your specific use case.

## Table of Contents

1. [Understanding the Current Implementation](#understanding-the-current-implementation)
2. [What Are Similarity Thresholds?](#what-are-similarity-thresholds)
3. [When to Tune Search Parameters](#when-to-tune-search-parameters)
4. [Step-by-Step Tuning Guide](#step-by-step-tuning-guide)
5. [Real-World Examples](#real-world-examples)
6. [Trade-offs and Considerations](#trade-offs-and-considerations)
7. [Advanced Tuning](#advanced-tuning)

---

## Understanding the Current Implementation

### Default Configuration

Out of the box, AI Memory Service uses these search parameters:

**File:** `services/conversation_service.py` (line 179-181)

```python
# Hybrid search: 80% semantic, 20% text-based
documents = hybrid_search(query, vector_query, user_id, weight=0.8, top_n=5)

# Similarity threshold: 0.70 (moderate)
relevant_results = [doc for doc in documents if doc["score"] >= 0.70]
```

### What This Means

- **Weight = 0.8**: Search is 80% based on semantic meaning, 20% on keyword matching
- **top_n = 5**: MongoDB returns top 5 candidates from vector search
- **Threshold = 0.70**: Only show results with 70%+ similarity

**Why these defaults?**
- Balanced between precision (finding exact matches) and recall (finding related content)
- Works well for general-purpose conversational search
- Tolerant enough to find conceptually related content

---

## What Are Similarity Thresholds?

### The Similarity Score

MongoDB's vector search returns a **cosine similarity score** between 0 and 1:

| Score | Meaning | Example |
|-------|---------|---------|
| 0.95-1.00 | Nearly identical | "pizza" vs "pizza slice" |
| 0.85-0.94 | Very similar | "pizza" vs "pepperoni pizza" |
| 0.75-0.84 | Highly related | "pizza" vs "italian food" |
| 0.65-0.74 | Moderately related | "pizza" vs "dinner options" |
| 0.50-0.64 | Loosely related | "pizza" vs "restaurant" |
| < 0.50 | Weakly related | "pizza" vs "food delivery" |

### How Thresholds Filter Results

```python
# Example search results before filtering
results = [
    {"text": "I love pizza with pepperoni", "score": 0.92},
    {"text": "Let's order Italian food tonight", "score": 0.78},
    {"text": "The restaurant has great dinner specials", "score": 0.68},
    {"text": "We should get some groceries", "score": 0.52}
]

# With threshold = 0.70
filtered = [r for r in results if r["score"] >= 0.70]
# Returns: First 2 results (pizza, Italian food)

# With threshold = 0.80
filtered = [r for r in results if r["score"] >= 0.80]
# Returns: Only first result (pizza)
```

---

## When to Tune Search Parameters

### Scenario 1: Too Many Irrelevant Results

**Problem:** Searching for "pizza" returns results about "food", "dinner", "meals"

**Solution:** Increase threshold

```python
# Before (permissive)
relevant_results = [doc for doc in documents if doc["score"] >= 0.70]

# After (stricter)
relevant_results = [doc for doc in documents if doc["score"] >= 0.80]
```

**Result:** Only highly relevant results appear

---

### Scenario 2: Too Few Results / Missing Related Content

**Problem:** Searching for "ML models" returns nothing, even though conversations mention "machine learning algorithms"

**Solution:** Lower threshold or adjust weight

```python
# Before (strict)
relevant_results = [doc for doc in documents if doc["score"] >= 0.80]

# After (more permissive)
relevant_results = [doc for doc in documents if doc["score"] >= 0.65]
```

**Result:** Captures semantically similar phrases

---

### Scenario 3: Need More Semantic Understanding

**Problem:** Searching for "AI" doesn't find "artificial intelligence" or "neural networks"

**Solution:** Increase semantic weight

```python
# Before (balanced)
documents = hybrid_search(query, vector_query, user_id, weight=0.8, top_n=5)

# After (more semantic)
documents = hybrid_search(query, vector_query, user_id, weight=0.9, top_n=5)
```

**Result:** Better conceptual matching

---

### Scenario 4: Need Exact Keyword Matching

**Problem:** Searching for "AWS Lambda" returns results about "serverless" and "cloud functions" but you want exact matches

**Solution:** Decrease semantic weight

```python
# Before (semantic-focused)
documents = hybrid_search(query, vector_query, user_id, weight=0.8, top_n=5)

# After (keyword-focused)
documents = hybrid_search(query, vector_query, user_id, weight=0.5, top_n=5)
```

**Result:** More literal keyword matching

---

## Step-by-Step Tuning Guide

### Step 1: Identify Your Use Case

**Question:** What type of search behavior do you need?

| Use Case | Recommended Settings |
|----------|---------------------|
| **Precise matching** (technical docs, codes, exact terms) | Threshold: 0.85+, Weight: 0.6 |
| **General search** (conversations, notes) | Threshold: 0.70, Weight: 0.8 |
| **Broad discovery** (exploring topics) | Threshold: 0.60, Weight: 0.9 |
| **Strict relevance** (only very similar) | Threshold: 0.90+, Weight: 0.9 |

### Step 2: Test Current Behavior

```bash
# Start your backend
python3 main.py

# In another terminal, test search
curl "http://localhost:8182/retrieve_memory/?user_id=test&text=pizza"
```

**Evaluate:**
- Are results too broad or too narrow?
- Are you missing expected results?
- Are irrelevant results appearing?

### Step 3: Make Incremental Changes

**Rule of thumb:** Change one parameter at a time by small amounts

```python
# Start with current defaults
threshold = 0.70
weight = 0.8
top_n = 5

# If too broad → increase threshold by 0.05
threshold = 0.75

# Test, then adjust again if needed
threshold = 0.80

# If missing results → decrease threshold or increase weight
threshold = 0.65
# OR
weight = 0.85
```

### Step 4: Document Your Changes

Keep track of what works:

```python
# services/conversation_service.py

# Configuration notes:
# - Increased threshold to 0.80 for stricter matching (2026-01-13)
# - Reason: Users wanted only closely related results for specific queries
# - Trade-off: May miss some loosely related content

relevant_results = [doc for doc in documents if doc["score"] >= 0.80]
```

---

## Real-World Examples

### Example 1: Customer Support Chatbot

**Goal:** Find exact solutions to customer problems

**Settings:**
```python
# High precision, moderate semantic understanding
documents = hybrid_search(query, vector_query, user_id, weight=0.7, top_n=3)
relevant_results = [doc for doc in documents if doc["score"] >= 0.85]
```

**Why:**
- Threshold 0.85: Only very similar issues
- Weight 0.7: Some semantic understanding but prefers exact keywords
- top_n 3: Show only best matches

---

### Example 2: Research Knowledge Base

**Goal:** Discover related concepts and papers

**Settings:**
```python
# High recall, strong semantic understanding
documents = hybrid_search(query, vector_query, user_id, weight=0.95, top_n=10)
relevant_results = [doc for doc in documents if doc["score"] >= 0.60]
```

**Why:**
- Threshold 0.60: Cast wider net
- Weight 0.95: Almost pure semantic search
- top_n 10: More candidates to choose from

---

### Example 3: Code Search

**Goal:** Find exact function/variable names

**Settings:**
```python
# Keyword-focused with high threshold
documents = hybrid_search(query, vector_query, user_id, weight=0.4, top_n=5)
relevant_results = [doc for doc in documents if doc["score"] >= 0.90]
```

**Why:**
- Threshold 0.90: Near-exact matches only
- Weight 0.4: Prefer keyword matching
- Exact names matter more than concepts

---

### Example 4: Personal Notes/Journal

**Goal:** Flexible search across thoughts and memories

**Settings:**
```python
# Balanced, permissive
documents = hybrid_search(query, vector_query, user_id, weight=0.8, top_n=7)
relevant_results = [doc for doc in documents if doc["score"] >= 0.65]
```

**Why:**
- Threshold 0.65: Find loosely related entries
- Weight 0.8: Good semantic understanding
- Personal context varies widely

---

## Trade-offs and Considerations

### Precision vs Recall

```
High Threshold (0.85+)
✅ Precision: Results are highly relevant
❌ Recall: May miss related content
Best for: Specific lookups, exact matches

Low Threshold (0.60-0.70)
❌ Precision: Some irrelevant results
✅ Recall: Finds more related content
Best for: Discovery, exploration
```

### Semantic vs Keyword Weight

```
High Semantic Weight (0.9+)
✅ Finds conceptually similar content
✅ Handles synonyms well
❌ May miss exact terms
❌ Slower (more embedding comparisons)

Low Semantic Weight (0.5-)
✅ Finds exact keyword matches
✅ Faster (less vector computation)
❌ Misses paraphrased content
❌ Less intelligent matching
```

### Performance Impact

```python
# Faster queries (less work)
top_n = 3              # Fewer candidates
weight = 0.5           # Less vector search
threshold = 0.85       # Quick filtering

# Slower queries (more work)
top_n = 20             # More candidates
weight = 0.95          # Heavy vector search
threshold = 0.50       # More results to process
```

---

## Advanced Tuning

### Dynamic Thresholds Based on Query

```python
async def search_memory(user_id, query):
    """Smart threshold based on query characteristics"""
    
    vector_query = generate_embedding(query)
    
    # Short queries = stricter (probably looking for something specific)
    if len(query.split()) <= 2:
        threshold = 0.85
        weight = 0.7
    # Longer queries = more permissive (exploratory)
    else:
        threshold = 0.70
        weight = 0.9
    
    documents = hybrid_search(query, vector_query, user_id, weight=weight, top_n=5)
    relevant_results = [doc for doc in documents if doc["score"] >= threshold]
    
    # ... rest of function
```

### User-Specific Tuning

```python
# Allow users to adjust their own search sensitivity
user_preferences = {
    "alice": {"threshold": 0.80, "weight": 0.9},  # Wants semantic search
    "bob": {"threshold": 0.75, "weight": 0.6},    # Wants keyword focus
}

def get_user_search_params(user_id):
    return user_preferences.get(user_id, {
        "threshold": 0.70,  # Default
        "weight": 0.8
    })
```

### A/B Testing Search Parameters

```python
import random

async def search_memory(user_id, query):
    # 50% of searches use new settings for testing
    if random.random() < 0.5:
        threshold = 0.80  # Experimental
        weight = 0.85
        variant = "B"
    else:
        threshold = 0.70  # Control
        weight = 0.8
        variant = "A"
    
    # Log for analysis
    logger.info(f"Search variant {variant} for user {user_id}")
    
    # ... perform search
```

---

## Tuning Checklist

Before changing parameters, ask:

- [ ] What problem am I trying to solve?
  - Too many irrelevant results?
  - Missing expected results?
  - Need faster searches?

- [ ] What is my use case?
  - Technical/precise vs general/exploratory?
  - User expectations for search behavior?

- [ ] Have I tested incrementally?
  - Changed one parameter at a time?
  - Tested with real queries?
  - Compared before/after results?

- [ ] Have I documented changes?
  - Why the change was made?
  - What the trade-offs are?
  - How to revert if needed?

---

## Quick Reference

### Parameter Guide

```python
# In services/conversation_service.py

# Line ~179
documents = hybrid_search(
    query,           # Search query text
    vector_query,    # Embedding vector
    user_id,         # User to search
    weight=0.8,      # 0.0-1.0: Semantic weight (higher = more semantic)
    top_n=5          # Number of candidates (1-20 typical)
)

# Line ~181
relevant_results = [
    doc for doc in documents 
    if doc["score"] >= 0.70  # 0.0-1.0: Minimum similarity (higher = stricter)
]
```

### Common Adjustments

| Goal | Change | Value |
|------|--------|-------|
| Stricter results | Increase threshold | 0.70 → 0.80 |
| More results | Decrease threshold | 0.70 → 0.60 |
| Better concept matching | Increase weight | 0.8 → 0.9 |
| Better keyword matching | Decrease weight | 0.8 → 0.6 |
| Faster searches | Decrease top_n | 5 → 3 |
| More candidates | Increase top_n | 5 → 10 |

---

## Testing Your Changes

### Manual Testing

```bash
# Test search with various queries
curl "http://localhost:8182/retrieve_memory/?user_id=test&text=pizza"
curl "http://localhost:8182/retrieve_memory/?user_id=test&text=machine+learning"
curl "http://localhost:8182/retrieve_memory/?user_id=test&text=AWS+Lambda"

# Check scores in results
curl -s "http://localhost:8182/retrieve_memory/?user_id=test&text=pizza" | jq '.related_conversation[].score'
```

### Evaluation Metrics

Track these over time:

1. **Precision**: What % of results are relevant?
2. **Recall**: Are you finding everything you should?
3. **User satisfaction**: Are users finding what they need?
4. **Performance**: How fast are searches?

---

## Next Steps

1. **Identify your use case** from the examples above
2. **Try recommended settings** for that use case
3. **Test with real queries** from your users
4. **Adjust incrementally** based on feedback
5. **Document what works** for future reference

---

## Resources

- [MongoDB Vector Search Docs](https://www.mongodb.com/docs/atlas/atlas-vector-search/tutorials/)
- [Understanding Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Advanced Optimizations](07-ADVANCED-OPTIMIZATIONS.md) - Performance tuning
- [Troubleshooting](05-TROUBLESHOOTING.md) - Search not working?

---

**Remember:** There's no "perfect" setting - it depends on your specific use case and user expectations. Start with the defaults, test thoroughly, and adjust based on real usage patterns.
