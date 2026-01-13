# Hints for Exercise 2: Index Health Monitoring

## Progressive Hints

### Hint 1: Getting Search Indexes

Use the `.list_search_indexes()` method on a collection:

```python
from database.mongodb import conversations, memory_nodes

# Get search indexes for conversations collection
search_indexes = list(conversations.list_search_indexes())

# Each index is a dict with 'name', 'type', etc.
for idx in search_indexes:
    print(idx['name'])
```

### Hint 2: Checking if Index Exists

```python
async def validate_search_indexes():
    from database.mongodb import conversations, memory_nodes
    
    # Get all search indexes
    conv_indexes = list(conversations.list_search_indexes())
    mem_indexes = list(memory_nodes.list_search_indexes())
    
    # Check if specific index exists
    conv_vector_exists = any(
        idx['name'] == 'conversations_vector_search_index' 
        for idx in conv_indexes
    )
    
    return {
        "conversations_vector_search_index": {
            "exists": conv_vector_exists,
            "collection": "conversations"
        },
        # ... more indexes
    }
```

### Hint 3: Required Index Names

These are the exact names to check:

```python
REQUIRED_INDEXES = {
    "conversations": [
        "conversations_vector_search_index",
        "conversations_fulltext_search_index"
    ],
    "memory_nodes": [
        "memory_nodes_vector_search_index"
    ]
}
```

### Hint 4: Health Check Integration

In `main.py`, update the health check:

```python
@app.get("/health")
async def health_check():
    from database.index_validator import get_index_status
    
    health_status = {
        "status": "healthy",
        "service": "AI-Memory-Service",
        "dependencies": {}
    }
    
    # Check indexes
    index_status = await get_index_status()
    health_status["dependencies"]["search_indexes"] = index_status
    
    # Set degraded if any index missing
    if any(status == "missing" for status in index_status.values()):
        health_status["status"] = "degraded"
    
    return health_status
```

### Hint 5: Setup Instructions

Generate helpful instructions:

```python
def get_setup_instructions(missing_indexes):
    instructions = "## Missing MongoDB Atlas Search Indexes\n\n"
    instructions += "The following indexes need to be created:\n\n"
    
    for idx_name in missing_indexes:
        instructions += f"- `{idx_name}`\n"
    
    instructions += "\n**How to create:**\n"
    instructions += "1. Go to MongoDB Atlas\n"
    instructions += "2. Select your cluster\n"
    instructions += "3. Click 'Search' tab\n"
    instructions += "4. Create Search Index\n"
    instructions += "\nSee: docs/03-MONGODB-ATLAS.md\n"
    
    return instructions
```

### Hint 6: Complete Solution Structure

```python
# database/index_validator.py

from database.mongodb import conversations, memory_nodes, db
from typing import Dict, List, Any

REQUIRED_INDEXES = {
    "conversations": [
        "conversations_vector_search_index",
        "conversations_fulltext_search_index"
    ],
    "memory_nodes": [
        "memory_nodes_vector_search_index"
    ]
}

async def validate_search_indexes() -> Dict[str, Any]:
    """Check all required indexes"""
    status = {}
    
    # Check conversations indexes
    conv_indexes = list(conversations.list_search_indexes())
    for idx_name in REQUIRED_INDEXES["conversations"]:
        exists = any(idx['name'] == idx_name for idx in conv_indexes)
        status[idx_name] = {
            "exists": exists,
            "collection": "conversations"
        }
    
    # Check memory_nodes indexes  
    mem_indexes = list(memory_nodes.list_search_indexes())
    for idx_name in REQUIRED_INDEXES["memory_nodes"]:
        exists = any(idx['name'] == idx_name for idx in mem_indexes)
        status[idx_name] = {
            "exists": exists,
            "collection": "memory_nodes"
        }
    
    return status

async def get_index_status() -> Dict[str, str]:
    """Get simple status"""
    full_status = await validate_search_indexes()
    return {
        name: "exists" if info["exists"] else "missing"
        for name, info in full_status.items()
    }

def get_setup_instructions(missing_indexes: List[str]) -> str:
    """Generate setup instructions"""
    # ... implementation
```

## Common Issues

**Issue 1:** Import error for `database.mongodb`
- Make sure `sys.path` includes parent directories

**Issue 2:** `.list_search_indexes()` not found
- This requires pymongo 4.0+ with Atlas support
- Check your pymongo version: `pip show pymongo`

**Issue 3:** Connection errors
- Ensure MongoDB connection is established before checking indexes
- Add try/except around index checks

## Testing Locally

Since you may not have Atlas Search indexes set up:

1. Mock the responses in tests (see `test_index_health.py`)
2. Use `monkeypatch` or `unittest.mock`
3. Test the logic, not the actual Atlas connection

## Next Steps

Once working, test with a real Atlas cluster to see the actual index status!
