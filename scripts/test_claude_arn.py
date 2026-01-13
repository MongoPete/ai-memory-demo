#!/usr/bin/env python3
"""
Simple script to test the Claude inference profile ARN.
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")
claude_arn = "arn:aws:bedrock:us-east-1:979559056307:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"

print("Testing Claude ARN...")
print(f"ARN: {claude_arn}")
print(f"Region: {region}\n")

try:
    bedrock = boto3.client("bedrock-runtime", region_name=region)
    
    response = bedrock.converse(
        modelId=claude_arn,
        messages=[{"role": "user", "content": [{"text": "Say hello in one word"}]}]
    )
    
    print("✅ SUCCESS! Claude model works!")
    print(f"Response: {response['output']['message']['content'][0]['text']}\n")
    print("You can use this ARN in your .env file:")
    print(f"LLM_MODEL_ID={claude_arn}")
    
except Exception as e:
    error_msg = str(e)
    if "UnrecognizedClientException" in error_msg:
        print("❌ Invalid credentials")
        print("   Please update your .env file with valid AWS credentials")
    elif "AccessDenied" in error_msg:
        print("❌ Access denied")
        print("   Your IAM user may not have Bedrock permissions")
    else:
        print(f"❌ Error: {error_msg}")
