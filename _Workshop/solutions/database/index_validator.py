"""
Index Validator Module

Checks MongoDB Atlas Search index health for production readiness.

This module demonstrates:
- Programmatic index validation
- Production readiness checks
- Clear error messaging
- Infrastructure health monitoring
"""

from database.mongodb import conversations, memory_nodes
from typing import Dict, List, Any
from utils.logger import logger

# Required Atlas Search indexes for the application
REQUIRED_INDEXES = {
    "conversations": [
        "conversations_vector_search_index",      # Vector search for semantic search
        "conversations_fulltext_search_index"     # Full-text search for keywords
    ],
    "memory_nodes": [
        "memory_nodes_vector_search_index"        # Vector search for memory similarity
    ]
}


async def validate_search_indexes() -> Dict[str, Any]:
    """
    Check if all required MongoDB Atlas Search indexes exist.
    
    Returns:
        Dictionary mapping index name to status info:
        {
            "index_name": {
                "exists": bool,
                "collection": str,
                "type": str (vector|search)
            }
        }
    """
    status = {}
    
    try:
        # Check conversations collection indexes
        conv_indexes = list(conversations.list_search_indexes())
        conv_index_names = [idx.get('name') for idx in conv_indexes]
        
        for idx_name in REQUIRED_INDEXES["conversations"]:
            exists = idx_name in conv_index_names
            idx_type = "vector" if "vector" in idx_name else "search"
            
            status[idx_name] = {
                "exists": exists,
                "collection": "conversations",
                "type": idx_type
            }
            
            if not exists:
                logger.warning(f"Missing search index: {idx_name}")
        
        # Check memory_nodes collection indexes
        mem_indexes = list(memory_nodes.list_search_indexes())
        mem_index_names = [idx.get('name') for idx in mem_indexes]
        
        for idx_name in REQUIRED_INDEXES["memory_nodes"]:
            exists = idx_name in mem_index_names
            
            status[idx_name] = {
                "exists": exists,
                "collection": "memory_nodes",
                "type": "vector"
            }
            
            if not exists:
                logger.warning(f"Missing search index: {idx_name}")
                
    except Exception as e:
        logger.error(f"Error validating search indexes: {e}")
        # Return error status for all indexes
        all_indexes = REQUIRED_INDEXES["conversations"] + REQUIRED_INDEXES["memory_nodes"]
        for idx_name in all_indexes:
            status[idx_name] = {
                "exists": False,
                "collection": "unknown",
                "error": str(e)
            }
    
    return status


async def get_index_status() -> Dict[str, str]:
    """
    Get simplified index status for health checks.
    
    Returns:
        Dictionary mapping index name to simple status:
        {"index_name": "exists" | "missing" | "error"}
    """
    full_status = await validate_search_indexes()
    
    simple_status = {}
    for name, info in full_status.items():
        if "error" in info:
            simple_status[name] = "error"
        elif info["exists"]:
            simple_status[name] = "exists"
        else:
            simple_status[name] = "missing"
    
    return simple_status


def get_setup_instructions(missing_indexes: List[str]) -> str:
    """
    Generate helpful setup instructions for missing indexes.
    
    Args:
        missing_indexes: List of missing index names
        
    Returns:
        Markdown-formatted instructions
    """
    if not missing_indexes:
        return "✅ All search indexes are configured correctly!"
    
    instructions = "# ⚠️ Missing MongoDB Atlas Search Indexes\n\n"
    instructions += "The following search indexes need to be created:\n\n"
    
    for idx_name in missing_indexes:
        instructions += f"- `{idx_name}`\n"
    
    instructions += "\n## How to Create Search Indexes\n\n"
    instructions += "### Option 1: MongoDB Atlas UI\n\n"
    instructions += "1. Log in to [MongoDB Atlas](https://cloud.mongodb.com)\n"
    instructions += "2. Navigate to your cluster\n"
    instructions += "3. Click the **Search** tab\n"
    instructions += "4. Click **Create Search Index**\n"
    instructions += "5. Follow the wizard for each missing index\n\n"
    
    instructions += "### Option 2: Atlas CLI\n\n"
    instructions += "```bash\n"
    instructions += "atlas clusters search indexes create \\\n"
    instructions += "  --clusterName <your-cluster> \\\n"
    instructions += "  --file index-definition.json\n"
    instructions += "```\n\n"
    
    instructions += "## Detailed Setup Guide\n\n"
    instructions += "See complete instructions: `docs/03-MONGODB-ATLAS.md`\n\n"
    
    instructions += "## Index Definitions\n\n"
    
    for idx_name in missing_indexes:
        if "vector" in idx_name:
            instructions += f"### {idx_name}\n"
            instructions += "```json\n"
            instructions += "{\n"
            instructions += f'  "name": "{idx_name}",\n'
            instructions += '  "type": "vectorSearch",\n'
            instructions += '  "definition": {\n'
            instructions += '    "fields": [{\n'
            instructions += '      "type": "vector",\n'
            instructions += '      "path": "embeddings",\n'
            instructions += '      "numDimensions": 1536,\n'
            instructions += '      "similarity": "cosine"\n'
            instructions += '    }]\n'
            instructions += '  }\n'
            instructions += "}\n"
            instructions += "```\n\n"
        else:
            instructions += f"### {idx_name}\n"
            instructions += "```json\n"
            instructions += "{\n"
            instructions += f'  "name": "{idx_name}",\n'
            instructions += '  "definition": {\n'
            instructions += '    "mappings": {\n'
            instructions += '      "dynamic": false,\n'
            instructions += '      "fields": {\n'
            instructions += '        "text": {\n'
            instructions += '          "type": "string",\n'
            instructions += '          "analyzer": "lucene.standard"\n'
            instructions += '        }\n'
            instructions += '      }\n'
            instructions += '    }\n'
            instructions += '  }\n'
            instructions += "}\n"
            instructions += "```\n\n"
    
    return instructions


async def check_and_warn_indexes():
    """
    Check indexes on startup and log warnings.
    Call this in main.py startup event.
    """
    logger.info("Checking MongoDB Atlas Search indexes...")
    
    status = await get_index_status()
    missing = [name for name, stat in status.items() if stat == "missing"]
    
    if missing:
        logger.warning(f"Missing {len(missing)} search indexes: {', '.join(missing)}")
        logger.warning("Search functionality may be degraded")
        logger.info("Run health check for setup instructions: GET /health")
    else:
        logger.info("✅ All search indexes are healthy")
    
    return len(missing) == 0
