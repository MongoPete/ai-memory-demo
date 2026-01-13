#!/usr/bin/env python3
"""
Script to detect and test available AWS Bedrock models.
Helps identify which models your account has access to.
"""

import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")

print("=" * 60)
print("AWS Bedrock Model Detection")
print("=" * 60)
print(f"Region: {region}\n")

try:
    # Initialize Bedrock client
    bedrock = boto3.client("bedrock", region_name=region)
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
    
    print("✅ Bedrock clients initialized\n")
    
    # List all foundation models
    print("Fetching available foundation models...")
    response = bedrock.list_foundation_models()
    
    models = response.get("modelSummaries", [])
    print(f"Found {len(models)} total models\n")
    
    # Find embedding models
    print("=" * 60)
    print("EMBEDDING MODELS:")
    print("=" * 60)
    embedding_models = []
    for model in models:
        model_id = model.get("modelId", "")
        model_name = model.get("modelName", "")
        provider = model.get("providerName", "")
        
        if any(keyword in model_id.lower() or keyword in model_name.lower() 
               for keyword in ["embed", "titan", "embedding"]):
            embedding_models.append(model)
            print(f"  ✅ Model ID: {model_id}")
            print(f"     Name: {model_name}")
            print(f"     Provider: {provider}")
            print()
    
    if not embedding_models:
        print("  ⚠️  No embedding models found in foundation models list")
        print("     You may need to check inference profiles or request access\n")
    
    # Find Claude models
    print("=" * 60)
    print("CLAUDE MODELS:")
    print("=" * 60)
    claude_models = []
    for model in models:
        model_id = model.get("modelId", "")
        model_name = model.get("modelName", "")
        provider = model.get("providerName", "")
        
        if "claude" in model_id.lower() or "claude" in model_name.lower():
            claude_models.append(model)
            print(f"  ✅ Model ID: {model_id}")
            print(f"     Name: {model_name}")
            print(f"     Provider: {provider}")
            print()
    
    # Test Claude model with inference profile ARN
    print("=" * 60)
    print("TESTING CLAUDE MODEL:")
    print("=" * 60)
    claude_arn = "arn:aws:bedrock:us-east-1:979559056307:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    print(f"Testing ARN: {claude_arn}\n")
    
    try:
        test_response = bedrock_runtime.converse(
            modelId=claude_arn,
            messages=[{"role": "user", "content": [{"text": "Say hello"}]}]
        )
        print("✅ Claude model works!")
        print(f"   Response: {test_response['output']['message']['content'][0]['text']}\n")
    except Exception as e:
        print(f"❌ Claude model test failed: {e}\n")
    
    # Test embedding models
    if embedding_models:
        print("=" * 60)
        print("TESTING EMBEDDING MODELS:")
        print("=" * 60)
        for model in embedding_models[:3]:  # Test first 3
            model_id = model.get("modelId", "")
            print(f"Testing: {model_id}")
            try:
                test_response = bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps({"inputText": "test embedding"})
                )
                result = json.loads(test_response["body"].read())
                embedding_dim = len(result.get("embedding", []))
                print(f"  ✅ Works! Embedding dimension: {embedding_dim}")
            except Exception as e:
                error_msg = str(e)
                if "AccessDenied" in error_msg:
                    print(f"  ⚠️  Access denied (may need to request access)")
                else:
                    print(f"  ❌ Error: {error_msg[:100]}")
            print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    print(f"✅ Claude ARN: {claude_arn}")
    if embedding_models:
        recommended = embedding_models[0].get("modelId", "")
        print(f"✅ Recommended Embedding Model: {recommended}")
    else:
        print("⚠️  No embedding models found - you may need to:")
        print("   1. Request access in Bedrock Console")
        print("   2. Check inference profiles")
        print("   3. Contact your AWS administrator")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
