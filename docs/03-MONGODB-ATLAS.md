# MongoDB Atlas Configuration

Complete guide for setting up MongoDB Atlas with vector search capabilities.

## Overview

AI Memory Service requires MongoDB Atlas with:
- Vector Search indexes for semantic search
- Full-text Search indexes for keyword search
- Proper network access configuration

## Prerequisites

- MongoDB Atlas account (free tier sufficient)
- Cluster created and running
- Database user created with read/write permissions

## Creating Search Indexes

The application requires **3 search indexes** to function properly:

### Index 1: Conversations Vector Search

**Purpose:** Enables semantic search across all conversation messages

**Steps:**
1. Go to MongoDB Atlas → Browse Collections
2. Select database: `ai_memory`
3. Select collection: `conversations`
4. Click "Search" tab (or "Search Indexes")
5. Click "Create Search Index"
6. Choose **"Atlas Vector Search"**
7. Select **"JSON Editor"**
8. Paste this configuration:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embeddings",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```

9. **Index name:** `conversations_vector_search_index` (exact name required!)
10. Click "Create Search Index"

### Index 2: Conversations Full-Text Search

**Purpose:** Enables keyword-based search across messages

**Steps:**
1. In `conversations` collection
2. Create another Search Index
3. Choose **"Atlas Search"** (not Vector Search)
4. Select **"JSON Editor"**
5. Paste this configuration:

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "text": {
        "type": "string"
      },
      "user_id": {
        "type": "string"
      },
      "conversation_id": {
        "type": "string"
      }
    }
  }
}
```

6. **Index name:** `conversations_fulltext_search_index` (exact name required!)
7. Click "Create Search Index"

### Index 3: Memory Nodes Vector Search

**Purpose:** Enables semantic search across stored memory nodes

**Steps:**
1. Go to collection: `memory_nodes`
2. Click "Search" tab
3. Create **"Atlas Vector Search"** index
4. Select **"JSON Editor"**
5. Paste this configuration:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embeddings",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```

6. **Index name:** `memory_nodes_vector_search_index` (exact name required!)
7. Click "Create Search Index"

## Wait for Index Building

After creating indexes:
- Status will show **"Building..."**
- Wait **2-5 minutes** for completion
- Status will change to **"Active"**
- Application won't work until all 3 are **Active**

## Verify Indexes

### Check in Atlas UI

1. Go to Search Indexes tab for each collection
2. Verify all 3 indexes show **"Active"** status
3. Note the index names match exactly

### Test from Application

```bash
# Start backend
python3 main.py

# Send a test message
curl -X POST http://localhost:8182/conversation/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "conversation_id": "test",
    "type": "human",
    "text": "Testing vector search with machine learning"
  }'

# Wait 2 seconds for indexing
sleep 2

# Search (should find the message)
curl "http://localhost:8182/retrieve_memory/?user_id=test&text=AI+models"
```

If you get results, indexes are working!

## Index Configuration Details

### Vector Search Parameters

**Dimensions: 1536**
- Matches AWS Titan embedding output
- Do not change this value

**Similarity: cosine**
- Best for text embeddings
- Range: -1 to 1 (higher = more similar)
- Alternative: euclidean, dotProduct

**Path: embeddings**
- Field name where vectors are stored
- Must match application code

### Full-Text Search Parameters

**Dynamic: false**
- Only index specified fields
- Better performance
- Explicit control

**Field types: string**
- Standard text search
- Case-insensitive by default

## Troubleshooting

### Index Build Fails

**Symptom:** Index stuck in "Building" or shows error

**Solutions:**
1. Delete the index and recreate
2. Check JSON syntax is correct (no trailing commas)
3. Verify collection has documents
4. Wait a bit longer (can take 5-10 min for large collections)

### Search Returns No Results

**Symptom:** Query works but returns empty array

**Possible causes:**
1. **Index not Active** - Check status in Atlas
2. **Wrong index name** - Names must match exactly
3. **No documents indexed yet** - Send some messages first
4. **Threshold too high** - App filters results <0.70 similarity

**Debug:**
```bash
# Check if documents exist
curl http://localhost:8182/memories/test

# Check backend logs for errors
# Look for "IndexNotFound" or similar

# Verify index names in code match Atlas
grep -r "vector_search_index" config.py
```

### Wrong Dimensions Error

**Error:** `VectorSearchIndexMismatch: dimensions don't match`

**Solution:**
- Index must be 1536 dimensions
- Delete and recreate with correct value
- Cannot be changed after creation

## Network Access

### IP Whitelist

MongoDB Atlas requires IP whitelisting:

**For Development:**
```
0.0.0.0/0 - Allow access from anywhere
```

**For Production:**
```
Your specific IP or CIDR range
Example: 203.0.113.0/24
```

**To update:**
1. MongoDB Atlas → Network Access
2. Add IP Address
3. Enter IP or select current IP
4. Confirm

### Connection String Format

Correct format:
```
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

**Common mistakes:**
- Missing `mongodb+srv://` prefix
- Special characters in password not URL-encoded
- Missing `/` after cluster name
- Wrong cluster hostname

**URL encode special characters:**
```
! → %21
@ → %40
# → %23
$ → %24
% → %25
```

Example:
```
Password: Pass@2024!
Encoded: Pass%402024%21
```

## Index Maintenance

### Monitor Index Usage

Atlas provides metrics:
- Operations per second
- Query latency
- Index size

**To view:**
1. Atlas → Database → Metrics
2. Look at "Search Index" tab
3. Monitor performance over time

### Rebuild Indexes

If indexes become corrupted or slow:

1. Note current configuration (export JSON)
2. Delete index
3. Recreate with same configuration
4. Wait for rebuild

**No downtime needed** - application continues working

### Scale Considerations

**Free Tier (M0):**
- 512MB storage
- ~1000-5000 documents
- Sufficient for demos

**Shared Tier (M2/M5):**
- More storage
- Better performance
- Suitable for dev/staging

**Dedicated (M10+):**
- Production workloads
- Custom sharding
- Advanced features

## Collection Indexes (Standard)

In addition to Search Indexes, create standard indexes:

```javascript
// In conversations collection
db.conversations.createIndex({ "user_id": 1, "conversation_id": 1, "timestamp": 1 })
db.conversations.createIndex({ "user_id": 1 })

// In memory_nodes collection
db.memory_nodes.createIndex({ "user_id": 1, "importance": -1 })
db.memory_nodes.createIndex({ "user_id": 1, "timestamp": -1 })
```

These improve query performance for:
- Retrieving user conversations
- Sorting by importance
- Timestamp-based queries

## Best Practices

1. **Create indexes before adding data** - Faster than retroactive indexing
2. **Monitor index size** - Large indexes affect query performance
3. **Test with sample data** - Verify indexes work before production
4. **Use exact index names** - Application expects specific names
5. **Document changes** - Keep track of index configurations
6. **Regular backups** - Atlas provides automatic backups

## Performance Tuning

### Query Performance

Hybrid search parameters in code:
```python
weight=0.8          # Vector vs text weight (0.0-1.0)
top_n=5             # Number of results
numCandidates=200   # Vector search candidates
```

Adjust based on:
- Result quality
- Query latency
- Resource usage

### Index Optimization

For production:
- Monitor slow queries in Atlas
- Adjust numCandidates based on load
- Consider separate indexes for different use cases
- Use compound indexes where appropriate

## Additional Resources

- [MongoDB Atlas Vector Search Docs](https://www.mongodb.com/docs/atlas/atlas-vector-search/overview/)
- [MongoDB Atlas Search Docs](https://www.mongodb.com/docs/atlas/atlas-search/)
- [Vector Search Tutorial](https://www.mongodb.com/docs/atlas/atlas-vector-search/tutorials/)

## Quick Reference

**Required indexes:**
1. `conversations_vector_search_index` - Vector (1536 dim, cosine)
2. `conversations_fulltext_search_index` - Full-text (text, user_id)
3. `memory_nodes_vector_search_index` - Vector (1536 dim, cosine)

**Index build time:** 2-5 minutes each

**Must be Active before app works properly**

---

**Next:** [AWS Bedrock Setup](04-AWS-BEDROCK.md)
