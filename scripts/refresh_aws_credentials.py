#!/usr/bin/env python3
"""
Auto-refresh AWS session tokens and update .env file
Supports AWS SSO and other credential refresh methods
"""

import os
import subprocess
import re
from pathlib import Path

def get_env_file_path():
    """Get path to .env file"""
    return Path(__file__).parent.parent / ".env"

def refresh_aws_sso_credentials():
    """Refresh AWS SSO credentials"""
    try:
        print("🔄 Attempting AWS SSO login...")
        # Run AWS SSO login
        result = subprocess.run(
            ["aws", "sso", "login"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ AWS SSO login failed: {result.stderr}")
            return None
        
        print("✅ AWS SSO login successful")
        
        # Get credentials from AWS CLI
        print("📥 Exporting credentials...")
        creds_result = subprocess.run(
            ["aws", "configure", "export-credentials", "--format", "env"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if creds_result.returncode != 0:
            print(f"❌ Failed to export credentials: {creds_result.stderr}")
            return None
        
        # Parse credentials
        credentials = {}
        for line in creds_result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                # Remove export keyword if present
                key = key.replace('export ', '').strip()
                # Remove quotes
                value = value.strip('"').strip("'")
                credentials[key] = value
        
        return credentials
    except subprocess.TimeoutExpired:
        print("❌ Timeout waiting for AWS SSO login")
        return None
    except FileNotFoundError:
        print("❌ AWS CLI not found. Install it: https://aws.amazon.com/cli/")
        return None
    except Exception as e:
        print(f"❌ Error refreshing credentials: {e}")
        return None

def update_env_file(credentials):
    """Update .env file with new credentials"""
    env_path = get_env_file_path()
    
    if not env_path.exists():
        print(f"❌ .env file not found at {env_path}")
        return False
    
    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Track which credentials we've updated
    updated = {
        'AWS_ACCESS_KEY_ID': False,
        'AWS_SECRET_ACCESS_KEY': False,
        'AWS_SESSION_TOKEN': False,
    }
    
    # Update existing lines
    new_lines = []
    for line in lines:
        for key in updated.keys():
            if line.strip().startswith(f'{key}='):
                new_lines.append(f'{key}={credentials.get(key, "")}\n')
                updated[key] = True
                break
        else:
            new_lines.append(line)
    
    # Add missing credentials at the end
    for key, was_updated in updated.items():
        if not was_updated and credentials.get(key):
            new_lines.append(f'{key}={credentials.get(key)}\n')
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Updated {env_path} with new credentials")
    return True

def check_credentials_valid():
    """Check if current credentials are valid"""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def main():
    print("=" * 60)
    print("AWS Credentials Auto-Refresh")
    print("=" * 60)
    print()
    
    # Check if credentials are already valid
    if check_credentials_valid():
        print("✅ Current credentials are still valid")
        print("   No refresh needed")
        return 0
    
    print("⚠️  Credentials expired or invalid")
    print()
    
    # Refresh credentials
    credentials = refresh_aws_sso_credentials()
    
    if not credentials:
        print()
        print("❌ Failed to refresh credentials")
        print("   You may need to:")
        print("   1. Run 'aws sso login' manually")
        print("   2. Or update .env file with new credentials")
        return 1
    
    # Update .env file
    if update_env_file(credentials):
        print()
        print("✅ Credentials refreshed and .env updated!")
        print()
        print("⚠️  Restart backend to use new credentials:")
        print("   pkill -f 'python3 main.py'")
        print("   python3 main.py")
        return 0
    else:
        print()
        print("❌ Failed to update .env file")
        return 1

if __name__ == "__main__":
    exit(main())
