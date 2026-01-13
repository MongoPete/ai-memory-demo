# Exercise 2: Index Health Monitoring

**Time Estimate:** 30-40 minutes  
**Difficulty:** ⭐⭐⭐ Intermediate

## Learning Objectives

By completing this exercise, you will:
- Understand MongoDB Atlas Search indexes and how they differ from regular indexes
- Learn to programmatically check index existence
- Implement production readiness checks for AI applications
- Practice defensive error handling for missing infrastructure

## Problem Statement

The current demo fails silently if MongoDB Atlas Search indexes don't exist. Users see cryptic errors like:

```
MongoServerError: $search stage is only allowed on a replica set or sharded cluster
```

Or worse - no error at all, just no search results!

### Why This Matters

MongoDB Atlas Search indexes must be created **manually** in the Atlas UI. They are NOT created automatically like regular MongoDB indexes. This means:

1. Fresh deployments fail silently
2. Debugging is extremely difficult  
3. Users don't know what's wrong
4. Production readiness is unclear

## Your Task

Create an `index_validator.py` module that checks if required search indexes exist and provides helpful feedback.

### Requirements

#### Part 1: Create `database/index_validator.py`

Implement these functions:

```python
async def validate_search_indexes() -> Dict[str, Any]:
    """
    Check if all required Atlas Search indexes exist.
    
    Returns:
        Dictionary with index status for each required index:
        {
            "conversations_vector_search_index": {
                "exists": True/False,
                "collection": "conversations",
                "type": "vectorSearch"
            },
            ...
        }
    """

async def get_index_status() -> Dict[str, str]:
    """
    Get simple status for each index.
    
    Returns:
        {"index_name": "exists" | "missing" | "error"}
    """

def get_setup_instructions(missing_indexes: List[str]) -> str:
    """
    Generate helpful instructions for creating missing indexes.
    
    Returns:
        Markdown-formatted instructions with links to docs
    """
```

#### Part 2: Enhance `/health` endpoint in `main.py`

Update the health check to include index status:

```json
{
  "status": "healthy",
  "service": "AI-Memory-Service",
  "dependencies": {
    "mongodb": "connected",
    "aws_bedrock": "available",
    "search_indexes": {
      "conversations_vector_search_index": "exists",
      "conversations_fulltext_search_index": "exists",
      "memory_nodes_vector_search_index": "missing"
    }
  }
}
```

If ANY index is missing, `status` should be `"degraded"`.

### Required Indexes

Your validator must check for these 3 indexes:

1. **`conversations_vector_search_index`**
   - Collection: `conversations`
   - Type: Vector Search
   - Dimensions: 1536
   - Path: `embeddings`

2. **`conversations_fulltext_search_index`**
   - Collection: `conversations`
   - Type: Search (Full-text)
   - Path: `text`

3. **`memory_nodes_vector_search_index`**
   - Collection: `memory_nodes`
   - Type: Vector Search
   - Dimensions: 1536
   - Path: `embeddings`

## File Structure

```
database/
├── __init__.py
├── mongodb.py
├── models.py
└── index_validator.py  # NEW - Create this
```

## Running Tests

```bash
cd /Users/peter.do/ai-memory/_Workshop/exercises/02-index-health
python -m pytest test_index_health.py -v
```

## Success Criteria

✅ `validate_search_indexes()` returns correct status for all indexes  
✅ `/health` endpoint shows index status  
✅ Missing indexes result in `"degraded"` status  
✅ Clear error messages with setup instructions  
✅ All tests pass

## MongoDB Context

### Atlas Search Indexes vs Regular Indexes

**Regular MongoDB Indexes** (`.createIndex()`):
- Created programmatically
- Managed via MongoDB driver
- Automatic in many ORMs
- Simple key-value indexing

**Atlas Search Indexes**:
- Created ONLY in Atlas UI or API
- Not accessible via standard MongoDB driver
- Support vector search, full-text search, facets
- Require special syntax (`$vectorSearch`, `$search`)

### Checking Index Existence

You can't use `.listIndexes()` for Atlas Search indexes. Instead:

```python
# Get list of search indexes
search_indexes = list(collection.list_search_indexes())

# Check if specific index exists
index_exists = any(idx['name'] == 'my_index' for idx in search_indexes)
```

### Production Implications

In production, you should:
1. ✅ Check indexes on startup
2. ✅ Include in health checks
3. ✅ Alert if indexes missing
4. ✅ Provide clear setup docs
5. ✅ Consider Infrastructure-as-Code (Terraform/Pulumi)

## Hints

Need help? Check `hints.md` in this directory.

## Next Steps

After completing this exercise:
1. Test your health check with and without indexes
2. Try the setup instructions on a fresh Atlas cluster
3. Read about Atlas Search architecture
4. Move on to Exercise 3: Pagination

---

**Pro Tip:** In production, use the Atlas Admin API to create indexes programmatically as part of your deployment pipeline!
