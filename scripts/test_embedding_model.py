#!/usr/bin/env python3
"""
Test script for embedding models.
Update the model_id variable with your embedding model ID/ARN.
"""

import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")

# Try these common embedding models (update with your actual model)
test_models = [
    "amazon.titan-embed-text-v1",
    "arn:aws:bedrock:us-east-1:979559056307:inference-profile/amazon.titan-embed-text-v1:0",
    # Add more models to test here
]

print("Testing Embedding Models...")
print(f"Region: {region}\n")

bedrock = boto3.client("bedrock-runtime", region_name=region)

for model_id in test_models:
    print(f"Testing: {model_id}")
    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({"inputText": "test embedding"})
        )
        result = json.loads(response["body"].read())
        embedding = result.get("embedding", [])
        print(f"  ✅ SUCCESS!")
        print(f"  Embedding dimension: {len(embedding)}")
        print(f"  Use this in your .env: EMBEDDING_MODEL_ID={model_id}\n")
        break
    except Exception as e:
        error_msg = str(e)
        if "UnrecognizedClientException" in error_msg:
            print(f"  ❌ Invalid credentials")
        elif "AccessDenied" in error_msg or "ModelNotFoundError" in error_msg:
            print(f"  ⚠️  Not available: {error_msg[:80]}")
        else:
            print(f"  ❌ Error: {error_msg[:80]}")
        print()

print("\nIf none worked, check AWS Console for available embedding models.")
print("See FIND-EMBEDDING-MODEL.md for more help.")
