import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

import config
from database.mongodb import initialize_mongodb, check_mongodb_connection
from services.bedrock_service import generate_embedding, check_bedrock_availability

# Import models and services
from models.pydantic_models import ErrorResponse, MessageInput
from services.conversation_service import (
    add_conversation_message,
    generate_conversation_summary,
    get_conversation_context,
    search_memory,
    get_conversation_history,
)
from services.memory_service import find_similar_memories, list_all_memories
from utils import error_utils

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description=config.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB on startup
initialize_mongodb()


@app.get("/health")
async def health_check():
    """
    Enhanced health check with dependency status.
    Returns service status and connectivity to MongoDB and AWS Bedrock.
    """
    health_status = {
        "status": "healthy",
        "service": config.APP_NAME,
        "version": config.APP_VERSION,
        "dependencies": {}
    }
    
    # Check MongoDB
    try:
        mongo_ok = await check_mongodb_connection()
        health_status["dependencies"]["mongodb"] = "connected" if mongo_ok else "disconnected"
        if not mongo_ok:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["dependencies"]["mongodb"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check AWS Bedrock (non-blocking - don't mark as degraded if unavailable)
    try:
        bedrock_ok = await check_bedrock_availability()
        health_status["dependencies"]["aws_bedrock"] = "available" if bedrock_ok else "unavailable"
    except Exception as e:
        health_status["dependencies"]["aws_bedrock"] = f"error: {str(e)}"
        # Don't mark as degraded for Bedrock - it's checked on-demand
    
    return health_status


@app.get("/memories/{user_id}")
async def get_memories(user_id: str):
    """
    Get all memories for a user. Returns list of memory nodes sorted by importance.
    """
    try:
        memories = await list_all_memories(user_id)
        return memories
    except HTTPException:
        raise
    except Exception as error:
        error_response = error_utils.handle_exception(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(**error_response).dict(),
        )

@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, user_id: str):
    """
    Get all messages in a conversation for display in chat view.
    Returns chronological list of messages.
    """
    try:
        messages = await get_conversation_history(user_id, conversation_id)
        return messages
    except HTTPException:
        raise
    except Exception as error:
        error_response = error_utils.handle_exception(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(**error_response).dict(),
        )


@app.post("/conversation/")
async def add_message(message: MessageInput):
    """Add a message to the conversation history"""
    try:
        return await add_conversation_message(message)
    except HTTPException:
        raise
    except Exception as error:
        error_response = error_utils.handle_exception(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(**error_response).dict(),
        )


@app.get("/retrieve_memory/")
async def retrieve_memory(user_id: str, text: str):
    """
    Retrieve memory items, context, summary, and similar memory nodes in a single request
    """
    try:
        # Generate embedding for the query text
        vector_query = generate_embedding(text)

        # Search for relevant memory items
        memory_items = await search_memory(user_id, text)

        # Get similar memory nodes from the memory tree
        similar_memories = await find_similar_memories(user_id, vector_query)

        if memory_items["documents"] == "No documents found":
            return {
                "related_conversation": "No conversation found",
                "conversation_summary": "No summary found",
                "similar_memories": (
                    similar_memories
                    if similar_memories
                    else "No similar memories found"
                ),
            }

        # Extract conversation ID from the first memory item
        object_id = memory_items["documents"][0]["_id"]

        # Retrieve conversation context around the matching memory item
        context = await get_conversation_context(object_id)

        # Generate a detailed summary for the conversation
        summary = await generate_conversation_summary(context["documents"])

        memories = [
            {
                "content": memory["content"],
                "summary": memory["summary"],
                "similarity": memory["similarity"],
                "importance": memory["effective_importance"],
            }
            for memory in similar_memories
        ]

        result = {
            "related_conversation": context["documents"],
            "conversation_summary": summary["summary"],
            "similar_memories": memories if memories else "No similar memories found",
        }

        return result
    except HTTPException:
        raise
    except Exception as error:
        error_response = error_utils.handle_exception(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(**error_response).dict(),
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.SERVICE_HOST,
        port=config.SERVICE_PORT,
        reload=config.DEBUG,
    )
