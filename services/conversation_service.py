import json
import datetime
import pymongo
from bson.objectid import ObjectId
from bson import json_util
from database.mongodb import conversations
from database.models import Message
from services.bedrock_service import generate_embedding, send_to_bedrock
from models.pydantic_models import RememberRequest
from services.memory_service import remember_content
from utils.logger import logger
import config

def hybrid_search(query, vector_query, user_id, weight=0.5, top_n=10):
    """
    Perform a hybrid search operation on MongoDB by combining full-text and vector (semantic) search results.
    """
    pipeline = [
        {
            "$search": {
                "index":config.CONVERSATIONS_FULLTEXT_SEARCH_INDEX_NAME,
                "text": {"query": query, "path": "text"},
            }
        },
        {"$match": {"user_id": user_id}},
        {"$addFields": {"fts_score": {"$meta": "searchScore"}}},
        {"$setWindowFields": {"output": {"maxScore": {"$max": "$fts_score"}}}},
        {
            "$addFields": {
                "normalized_fts_score": {"$divide": ["$fts_score", "$maxScore"]}
            }
        },
        {
            "$project": {
                "text": 1,
                "type": 1,
                "timestamp": 1,
                "conversation_id": 1,
                "normalized_fts_score": 1,
            }
        },
        {
            "$unionWith": {
                "coll": "conversations",
                "pipeline": [
                    {
                        "$vectorSearch": {
                            "index": config.CONVERSATIONS_VECTOR_SEARCH_INDEX_NAME,
                            "queryVector": vector_query,
                            "path": "embeddings",
                            "numCandidates": 200,
                            "limit": top_n,
                            "filter": {"user_id": user_id},
                        }
                    },
                    {"$addFields": {"vs_score": {"$meta": "vectorSearchScore"}}},
                    {
                        "$setWindowFields": {
                            "output": {"maxScore": {"$max": "$vs_score"}}
                        }
                    },
                    {
                        "$addFields": {
                            "normalized_vs_score": {
                                "$divide": ["$vs_score", "$maxScore"]
                            }
                        }
                    },
                    {
                        "$project": {
                            "text": 1,
                            "type": 1,
                            "timestamp": 1,
                            "conversation_id": 1,
                            "normalized_vs_score": 1,
                        }
                    },
                ],
            }
        },
        {
            "$group": {
                "_id": "$_id",  # Group by document ID
                "fts_score": {"$max": "$normalized_fts_score"},
                "vs_score": {"$max": "$normalized_vs_score"},
                "text_field": {"$first": "$text"},
                "type_field": {"$first": "$type"},
                "timestamp_field": {"$first": "$timestamp"},
                "conversation_id_field": {"$first": "$conversation_id"},
            }
        },
        {
            "$addFields": {
                "hybrid_score": {
                    "$add": [
                        {"$multiply": [weight, {"$ifNull": ["$vs_score", 0]}]},
                        {"$multiply": [1 - weight, {"$ifNull": ["$fts_score", 0]}]},
                    ]
                }
            }
        },
        {"$sort": {"hybrid_score": -1}},  # Sort by combined hybrid score descending
        {"$limit": top_n},  # Limit final output
        {
            "$project": {
                "_id": 1,
                "fts_score": 1,
                "vs_score": 1,
                "score": "$hybrid_score",
                "text": "$text_field",
                "type": "$type_field",
                "timestamp": "$timestamp_field",
                "conversation_id": "$conversation_id_field",
            }
        },
    ]
    # Execute the aggregation pipeline and return the results
    try:
        results = list(conversations.aggregate(pipeline))
        return results
    except Exception as e:
        logger.error(f"Error in hybrid_search: {e}")
        raise

async def add_conversation_message(message_input):
    """Add a message to the conversation history"""
    try:
        # Normalize user_id to lowercase for case-insensitive search
        message_input.user_id = message_input.user_id.lower()
        
        new_message = Message(message_input)
        conversations.insert_one(new_message.to_dict())
        # For significant human messages, create a memory node
        # Note: Memory creation is non-blocking - if it fails, message is still stored
        if message_input.type == "human" and len(message_input.text) > 30:
            try:
                memory_content = (
                    f"From conversation {message_input.conversation_id}: {message_input.text}"
                )
                logger.info(f"Creating memory for user {message_input.user_id}: {memory_content}")
                await remember_content(
                    RememberRequest(user_id=message_input.user_id, content=memory_content)
                )
            except Exception as memory_error:
                # Log error but don't fail message creation
                # Memory creation requires Bedrock - if unavailable, message still succeeds
                logger.warning(f"Memory creation failed (Bedrock may be unavailable): {str(memory_error)}")
                logger.info("Message stored successfully, but memory creation skipped")
        return {"message": "Message added successfully"}
    except Exception as error:
        logger.error(str(error))
        raise

async def search_memory(user_id, query):
    """
    Searches memory items using MongoDB Atlas hybrid search (vector + full-text).
    
    DEMO SHOWCASE:
    - Primary: Hybrid Search (AWS Bedrock embeddings + MongoDB Atlas full-text)
    - Fallback: MongoDB Atlas full-text search only (if Bedrock unavailable)
    
    This demonstrates MongoDB's powerful search capabilities both with and without vector embeddings.
    """
    try:
        # Normalize user_id to lowercase for case-insensitive matching
        user_id = user_id.lower()
        
        # Generate embedding for the query text using AWS Bedrock
        vector_query = generate_embedding(query)
        
        # FALLBACK PATH: MongoDB Atlas Full-Text Search Only
        # If embeddings unavailable (Bedrock down), leverage MongoDB's full-text search
        if not vector_query:
            logger.warning(f"Bedrock unavailable - using MongoDB Atlas full-text search only")
            logger.info(f"DEMO MODE: Showcasing MongoDB Atlas Search without vector embeddings")
            
            # Audit log: Track search type for analytics
            try:
                from database.mongodb import db
                audit_collection = db.get_collection("search_audit")
                audit_collection.insert_one({
                    "timestamp": datetime.datetime.now(datetime.timezone.utc),
                    "user_id": user_id,
                    "query": query,
                    "search_type": "atlas_fulltext_only",
                    "reason": "bedrock_embeddings_unavailable",
                    "note": "Using MongoDB Atlas Search index without vector component"
                })
            except Exception as audit_error:
                logger.debug(f"Audit logging failed (non-critical): {audit_error}")
            
            # MongoDB Atlas Full-Text Search Pipeline
            # Uses the same search index but only the text component
            MINIMUM_FULLTEXT_SCORE = 5.0  # Atlas Search scores are typically 0-15+ range
            pipeline = [
                {
                    "$search": {
                        "index": config.CONVERSATIONS_FULLTEXT_SEARCH_INDEX_NAME,
                        "text": {
                            "query": query,
                            "path": "text"
                        }
                    }
                },
                {"$match": {"user_id": user_id}},  # Filter by user (normalized to lowercase)
                {"$addFields": {"score": {"$meta": "searchScore"}}},  # Get search score
                {"$match": {"score": {"$gte": MINIMUM_FULLTEXT_SCORE}}},  # Filter low-relevance results
                {"$sort": {"score": -1}},  # Sort by relevance
                {"$limit": 10},  # Top 10 results
                {
                    "$project": {
                        "text": 1,
                        "type": 1,
                        "timestamp": 1,
                        "conversation_id": 1,
                        "score": 1,
                        "embeddings": 0  # Exclude embeddings from response
                    }
                }
            ]
            
            results = list(conversations.aggregate(pipeline))
            
            logger.info(f"MongoDB Atlas full-text search returned {len(results)} results above threshold")
            
            if not results:
                return {
                    "documents": "No documents found",
                    "search_metadata": {
                        "query": query,
                        "total_results": 0,
                        "relevant_results": 0,
                        "minimum_score": MINIMUM_FULLTEXT_SCORE,
                        "search_type": "atlas_fulltext_only",
                        "note": "Bedrock unavailable - using MongoDB Atlas full-text search only"
                    }
                }
            
            # Enrich results with score information
            enriched_results = []
            for doc in results:
                enriched_doc = serialize_document(doc)
                score = doc.get("score") or 0
                enriched_doc["relevance_scores"] = {
                    "fulltext_score": round(score, 4),
                    "explanation": f"Text relevance: {round(score, 2)}/15.0 (higher is better)"
                }
                enriched_results.append(enriched_doc)
            
            return {
                "documents": enriched_results,
                "search_metadata": {
                    "query": query,
                    "total_results": len(results),
                    "relevant_results": len(results),
                    "minimum_score": MINIMUM_FULLTEXT_SCORE,
                    "search_type": "atlas_fulltext_only",
                    "note": "Using MongoDB Atlas Search without vector embeddings (Bedrock unavailable)"
                }
            }
        
        # PRIMARY PATH: Hybrid Search (Vector + Full-Text)
        # This is the main showcase - combining AWS Bedrock embeddings with MongoDB Atlas Search
        logger.info("DEMO MODE: Using hybrid search (AWS Bedrock vectors + MongoDB Atlas full-text)")
        documents = hybrid_search(query, vector_query, user_id, weight=0.8, top_n=10)
        
        # ROBUST FILTERING: Filter results by minimum hybrid score threshold
        # Threshold of 0.70 ensures high-quality, relevant results
        # This prevents showing irrelevant results to users
        MINIMUM_HYBRID_SCORE = 0.70
        relevant_results = [doc for doc in documents if doc["score"] >= MINIMUM_HYBRID_SCORE]
        
        logger.info(f"Hybrid search: {len(documents)} total results, {len(relevant_results)} above threshold ({MINIMUM_HYBRID_SCORE})")
        
        if not relevant_results:
            logger.info(f"No results above relevance threshold for query: '{query}'")
            return {
                "documents": "No documents found",
                "search_metadata": {
                    "query": query,
                    "total_results": len(documents),
                    "relevant_results": 0,
                    "minimum_score": MINIMUM_HYBRID_SCORE,
                    "search_type": "hybrid_vector_fulltext",
                    "note": "No results met the minimum relevance threshold"
                }
            }
        
        # Enrich results with educational score breakdown
        enriched_results = []
        for doc in relevant_results:
            enriched_doc = serialize_document(doc)
            # Add detailed score breakdown for demo/educational purposes
            # Use 'or 0' to handle None values from MongoDB
            vs_score = doc.get("vs_score") or 0
            fts_score = doc.get("fts_score") or 0
            hybrid_score = doc.get("score") or 0
            
            enriched_doc["relevance_scores"] = {
                "hybrid_score": round(hybrid_score, 4),
                "vector_similarity": round(vs_score, 4),
                "fulltext_score": round(fts_score, 4),
                "explanation": f"Hybrid: {round(hybrid_score*100, 1)}% relevant (Vector: {round(vs_score*100, 1)}%, Text: {round(fts_score*100, 1)}%)"
            }
            enriched_results.append(enriched_doc)
        
        return {
            "documents": enriched_results,
            "search_metadata": {
                "query": query,
                "total_results": len(documents),
                "relevant_results": len(relevant_results),
                "minimum_score": MINIMUM_HYBRID_SCORE,
                "search_type": "hybrid_vector_fulltext",
                "weight_vector": 0.8,
                "weight_fulltext": 0.2,
                "note": "Results filtered by relevance threshold and ranked by hybrid score"
            }
        }
            
    except Exception as error:
        logger.error(f"Search failed: {str(error)}")
        raise

async def get_conversation_context(_id):
    """
    Fetches conversation records with context surrounding a specific message
    """
    try:
        # Fetch the conversation record for the given object ID
        conversation_record = conversations.find_one(
            {"_id": ObjectId(_id)},
            projection={
                "_id": 0,
                "embeddings": 0,
            },
        )
        if not conversation_record:
            return {"documents": "No documents found"}
        # Extract metadata
        user_id = conversation_record["user_id"]
        conversation_id = conversation_record["conversation_id"]
        timestamp = conversation_record["timestamp"]
        message_type = conversation_record["type"]
        if message_type == "ai":
            # Get more preceding context for AI messages
            prev_limit = 4
            next_limit = 2
        else:
            # Balance for human messages
            prev_limit = 3
            next_limit = 3
        # Get messages before target
        prev_cursor = (
            conversations.find(
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": {"$lte": timestamp},
                },
                projection={
                    "_id": 0,
                    "embeddings": 0,
                },
            )
            .sort("timestamp", pymongo.DESCENDING)
            .limit(prev_limit)
        )
        context = list(prev_cursor)
        # Get messages after target
        next_cursor = (
            conversations.find(
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": {"$gt": timestamp},
                },
                projection={
                    "_id": 0,
                    "embeddings": 0,
                },
            )
            .sort("timestamp", pymongo.ASCENDING)
            .limit(next_limit)
        )
        context_after = list(next_cursor)
        # Combine and sort all messages by timestamp
        conversation_with_context = sorted(
            context + context_after,
            key=lambda x: x["timestamp"],
        )
        return {"documents": conversation_with_context}
    except Exception as error:
        logger.error(str(error))
        raise

async def generate_conversation_summary(documents):
    """
    Generates a detailed and structured summary for a conversation provided in JSON format.
    """
    try:
        # Construct a prompt with detailed instructions and conversation history
        prompt = (
            f"You are an advanced AI assistant skilled in analyzing and summarizing conversation histories while preserving all essential details.\n"
            f"Given the following conversation data in JSON format, generate a detailed and structured summary that captures all key points, topics discussed, decisions made, and relevant insights.\n\n"
            f"Ensure your summary follows these guidelines:\n"
            f"- **Maintain Clarity & Accuracy:** Include all significant details, technical discussions, and conclusions.\n"
            f"- **Preserve Context & Meaning:** Avoid omitting important points that could alter the conversation's intent.\n"
            f"- **Organized Structure:** Present the summary in a logical flow or chronological order.\n"
            f"- **Key Highlights:** Explicitly state major questions asked, AI responses, decisions made, and follow-up discussions.\n"
            f"- **Avoid Redundancy:** Summarize effectively without unnecessary repetition.\n\n"
            f"### Output Format:\n"
            f"- **Topic:** Briefly describe the conversation's purpose.\n"
            f"- **Key Discussion Points:** Outline the main topics covered.\n"
            f"- **Decisions & Takeaways:** Highlight key conclusions or next steps.\n"
            f"- **Unresolved Questions (if any):** Mention pending queries or areas needing further clarification.\n\n"
            f"Provide a **clear, structured, and comprehensive** summary ensuring no critical detail is overlooked.\n\n"
            f"Input JSON: {json.dumps(documents, default=json_util.default)}"
        )
        # Send prompt to Bedrock and wait for summary response
        summary = await send_to_bedrock(prompt)
        return {"summary": summary}
    except Exception as error:
        logger.error(str(error))
        raise

async def get_conversation_history(user_id: str, conversation_id: str):
    """
    Fetch all messages in a conversation, sorted by timestamp.
    Returns a list of messages in chronological order.
    """
    try:
        # Normalize user_id to lowercase for case-insensitive search
        user_id = user_id.lower()
        
        cursor = conversations.find(
            {
                "user_id": user_id,
                "conversation_id": conversation_id
            },
            projection={
                "_id": 1,
                "user_id": 1,
                "conversation_id": 1,
                "type": 1,
                "text": 1,
                "timestamp": 1
            }
        ).sort("timestamp", pymongo.ASCENDING)
        
        messages = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            messages.append(doc)
        
        return messages
    except Exception as error:
        logger.error(f"Error fetching conversation history: {str(error)}")
        raise

def serialize_document(doc):
    """Helper function to serialize MongoDB documents."""
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc