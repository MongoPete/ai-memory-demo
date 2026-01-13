import json
import boto3
import asyncio
import os
from botocore.exceptions import ClientError, BotoCoreError
from config import AWS_REGION, EMBEDDING_MODEL_ID, LLM_MODEL_ID
from utils.logger import logger

# Initialize a shared boto3 client for Bedrock service
# Explicitly use credentials from environment (including session token)
def _get_bedrock_client():
    """Get Bedrock client with explicit credentials from environment"""
    client_kwargs = {"region_name": AWS_REGION}
    
    # Explicitly pass credentials if available (needed for session tokens)
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")
    
    if access_key and secret_key:
        client_kwargs["aws_access_key_id"] = access_key
        client_kwargs["aws_secret_access_key"] = secret_key
        if session_token:
            client_kwargs["aws_session_token"] = session_token
    
    return boto3.client("bedrock-runtime", **client_kwargs)

# Initialize client
try:
    bedrock_client = _get_bedrock_client()
    _bedrock_available = True
except Exception as e:
    logger.warning(f"Bedrock client initialization failed: {e}")
    bedrock_client = None
    _bedrock_available = False

async def check_bedrock_availability() -> bool:
    """Check if AWS Bedrock is available"""
    try:
        # Test by trying to use the actual models we need
        # This is more reliable than listing models which may require different permissions
        from config import EMBEDDING_MODEL_ID
        
        # Test embedding model (simpler test)
        test_bedrock = _get_bedrock_client()
        test_response = test_bedrock.invoke_model(
            modelId=EMBEDDING_MODEL_ID,
            body=json.dumps({"inputText": "test"})
        )
        # If we get here, Bedrock is available
        logger.info("Bedrock availability check: SUCCESS")
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        logger.warning(f"Bedrock availability check failed: {error_code} - {error_msg}")
        return False
    except Exception as e:
        logger.warning(f"Bedrock availability check failed: {type(e).__name__}: {e}")
        return False

def _refresh_credentials_if_needed():
    """Attempt to refresh credentials if they're expired"""
    try:
        import subprocess
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "refresh_aws_credentials.py")
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.dirname(script_path))
        )
        if result.returncode == 0:
            # Reload environment
            from dotenv import load_dotenv
            load_dotenv(override=True)
            logger.info("Credentials refreshed automatically")
            return True
    except Exception as e:
        logger.debug(f"Auto-refresh failed: {e}")
    return False

def generate_embedding(text: str) -> list:
    """
    Generate embeddings for text using AWS Bedrock's embedding model.
    Returns empty list if Bedrock is unavailable (graceful degradation).
    """
    if not text.strip():
        return []
    
    try:
        # Get fresh client to ensure credentials are up to date
        client = _get_bedrock_client()
        
        max_tokens = 8000  # Embedding model input token limit
        tokens = text.split()  # Simple tokenization by spaces
        text = " ".join(tokens[:max_tokens])  # Keep only allowed tokens
        payload = {"inputText": text}
        response = client.invoke_model(
            modelId=EMBEDDING_MODEL_ID, body=json.dumps(payload)
        )
        result = json.loads(response["body"].read())
        return result["embedding"]
    except (ClientError, BotoCoreError) as e:
        error_msg = str(e)
        # Check if credentials expired
        if "UnrecognizedClientException" in error_msg:
            logger.warning("Credentials expired, attempting auto-refresh...")
            if _refresh_credentials_if_needed():
                # Retry with fresh credentials
                try:
                    client = _get_bedrock_client()
                    max_tokens = 8000
                    tokens = text.split()
                    text = " ".join(tokens[:max_tokens])
                    payload = {"inputText": text}
                    response = client.invoke_model(
                        modelId=EMBEDDING_MODEL_ID, body=json.dumps(payload)
                    )
                    result = json.loads(response["body"].read())
                    logger.info("Successfully retried after credential refresh")
                    return result["embedding"]
                except Exception as retry_error:
                    logger.warning(f"Retry after refresh failed: {retry_error}")
        
        logger.warning(f"Failed to generate embeddings (Bedrock unavailable): {e}")
        # Return empty list to allow message storage without embeddings
        # Search will fall back to text-only search
        return []
    except Exception as e:
        logger.warning(f"Unexpected error generating embeddings: {e}")
        return []

async def send_to_bedrock(prompt):
    """
    Send a prompt to the Bedrock Claude model asynchronously.
    Returns None if Bedrock is unavailable (graceful degradation).
    """
    payload = [{"role": "user", "content": [{"text": prompt}]}]
    model_id = LLM_MODEL_ID
    try:
        # Get fresh client to ensure credentials are up to date
        client = _get_bedrock_client()
        
        # Use asyncio.to_thread to call the blocking boto3 client method
        response = await asyncio.to_thread(
            client.converse,
            modelId=model_id,
            messages=payload,
        )
        model_response = response["output"]["message"]
        # Concatenate text parts from the model response
        response_text = " ".join(i["text"] for i in model_response["content"])
        return response_text
    except (ClientError, BotoCoreError) as err:
        error_msg = str(err)
        error_code = err.response.get('Error', {}).get('Code', '') if hasattr(err, 'response') else ''
        
        # Check if credentials expired
        if "UnrecognizedClientException" in error_msg or error_code == "UnrecognizedClientException":
            logger.warning("Credentials expired, attempting auto-refresh...")
            if _refresh_credentials_if_needed():
                # Retry with fresh credentials
                try:
                    client = _get_bedrock_client()
                    response = await asyncio.to_thread(
                        client.converse,
                        modelId=model_id,
                        messages=payload,
                    )
                    model_response = response["output"]["message"]
                    response_text = " ".join(i["text"] for i in model_response["content"])
                    logger.info("Successfully retried after credential refresh")
                    return response_text
                except Exception as retry_error:
                    logger.warning(f"Retry after refresh failed: {retry_error}")
        
        error_msg_display = err.response.get('Error', {}).get('Message', str(err)) if hasattr(err, 'response') else str(err)
        logger.warning(f"Bedrock unavailable, cannot send prompt: {error_msg_display}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error sending to Bedrock: {e}")
        return None