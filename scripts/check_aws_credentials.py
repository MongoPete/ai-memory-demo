#!/usr/bin/env python3
"""
Check if AWS credentials are expired or invalid
"""

import boto3
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from botocore.exceptions import ClientError

def check_credentials():
    """Check if AWS credentials are valid"""
    # Load from project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
    
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    print("=" * 60)
    print("AWS Credentials Check")
    print("=" * 60)
    print()
    
    if not access_key or not secret_key:
        print("❌ Credentials not found in .env")
        print("   Missing AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY")
        return False
    
    print(f"✅ Access Key ID: {access_key[:10]}...")
    print(f"✅ Secret Key: {'*' * 20}")
    if session_token:
        print(f"✅ Session Token: Present")
    else:
        print(f"⚠️  Session Token: Not set (using permanent credentials)")
    print(f"✅ Region: {region}")
    print()
    
    try:
        # Test with Bedrock (what we actually use)
        client_kwargs = {"region_name": region}
        client_kwargs["aws_access_key_id"] = access_key
        client_kwargs["aws_secret_access_key"] = secret_key
        if session_token:
            client_kwargs["aws_session_token"] = session_token
        
        print("Testing Bedrock access...")
        bedrock = boto3.client("bedrock-runtime", **client_kwargs)
        
        # Try a simple call
        bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=json.dumps({"inputText": "test"})
        )
        
        print()
        print("✅ Credentials are valid and Bedrock is accessible!")
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        
        print()
        if error_code == 'UnrecognizedClientException':
            print("❌ Credentials expired or invalid")
            print(f"   Error: {error_msg}")
            print()
            print("💡 To refresh credentials:")
            print("   python3 scripts/refresh_aws_credentials.py")
        elif error_code == 'AccessDeniedException':
            print("❌ Access denied")
            print(f"   Error: {error_msg}")
            print()
            print("💡 Check IAM permissions for Bedrock")
        else:
            print(f"❌ Error: {error_code}")
            print(f"   {error_msg}")
        return False
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = check_credentials()
    sys.exit(0 if success else 1)
