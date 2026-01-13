import os
import sys
from typing import List, Tuple

def validate_required_env_vars() -> Tuple[bool, List[str]]:
    """
    Validate that all required environment variables are set.
    Returns (is_valid, missing_vars)
    """
    required_vars = {
        "MONGODB_URI": "MongoDB Atlas connection string",
        "AWS_ACCESS_KEY_ID": "AWS Access Key ID for Bedrock access",
        "AWS_SECRET_ACCESS_KEY": "AWS Secret Access Key for Bedrock access",
    }
    
    optional_vars = {
        "AWS_REGION": "us-east-1",
        "LLM_MODEL_ID": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "EMBEDDING_MODEL_ID": "amazon.titan-embed-text-v1",
        "DEBUG": "False",
        "SERVICE_HOST": "0.0.0.0",
        "SERVICE_PORT": "8182",
    }
    
    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} ({description})")
    
    if missing:
        # Use print instead of logger to avoid circular import
        print("ERROR: Missing required environment variables:", file=sys.stderr)
        for var in missing:
            print(f"  - {var}", file=sys.stderr)
        return False, missing
    
    return True, []

def validate_mongodb_uri(uri: str) -> bool:
    """Validate MongoDB URI format"""
    if not uri:
        return False
    return uri.startswith("mongodb://") or uri.startswith("mongodb+srv://")

def get_cors_origins() -> List[str]:
    """Get CORS allowed origins from environment or defaults"""
    cors_env = os.getenv("CORS_ORIGINS", "")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",")]
    
    # Default to common development ports
    return [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:5174",  # Vite HMR port
    ]
