#!/usr/bin/env python3
"""
AI Memory Service - Setup Validation Script
Comprehensive validation of all prerequisites and configuration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")

def print_check(text, status):
    """Print check result"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {text}")

def check_environment_variables():
    """Check required environment variables"""
    print("1. Checking environment variables...")
    print()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "MONGODB_URI": "MongoDB Atlas connection string",
        "AWS_ACCESS_KEY_ID": "AWS Access Key ID",
        "AWS_SECRET_ACCESS_KEY": "AWS Secret Access Key",
        "AWS_REGION": "AWS Region",
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value.strip():
            print_check(f"{var}: Set", True)
        else:
            print_check(f"{var}: Missing ({description})", False)
            all_present = False
    
    # Check optional but recommended
    llm_model = os.getenv("LLM_MODEL_ID")
    if llm_model:
        print_check("LLM_MODEL_ID: Set", True)
    else:
        print("⚠️  LLM_MODEL_ID: Not set (will use default)")
    
    embedding_model = os.getenv("EMBEDDING_MODEL_ID")
    if embedding_model:
        print_check("EMBEDDING_MODEL_ID: Set", True)
    else:
        print("⚠️  EMBEDDING_MODEL_ID: Not set (will use default)")
    
    print()
    return all_present

def check_mongodb_connection():
    """Test MongoDB connection"""
    print("2. Checking MongoDB Atlas connection...")
    print()
    
    try:
        from database.mongodb import client, check_mongodb_connection
        import asyncio
        
        # Test connection
        is_connected = asyncio.run(check_mongodb_connection())
        
        if is_connected:
            print_check("MongoDB connection successful", True)
            
            # Get server info
            info = client.server_info()
            version = info.get('version', 'unknown')
            print(f"   Server version: {version}")
            
            # Check database and collections
            db = client.get_database("ai_memory")
            collections = db.list_collection_names()
            print(f"   Collections: {', '.join(collections) if collections else 'None (will be created)'}")
            
            print()
            return True
        else:
            print_check("MongoDB connection failed", False)
            print("   Check: MongoDB URI, network access, cluster status")
            print()
            return False
            
    except Exception as e:
        print_check(f"MongoDB connection error: {str(e)}", False)
        print()
        return False

def check_aws_bedrock():
    """Test AWS Bedrock access"""
    print("3. Checking AWS Bedrock access...")
    print()
    
    try:
        from services.bedrock_service import check_bedrock_availability
        import asyncio
        
        is_available = asyncio.run(check_bedrock_availability())
        
        if is_available:
            print_check("AWS Bedrock accessible", True)
            
            # Test embedding generation
            from services.bedrock_service import generate_embedding
            test_embedding = generate_embedding("test")
            
            if test_embedding and len(test_embedding) > 0:
                print_check(f"Embedding generation working ({len(test_embedding)} dimensions)", True)
            else:
                print("⚠️  Embedding generation returned empty result")
            
            print()
            return True
        else:
            print_check("AWS Bedrock not accessible", False)
            print("   Check: AWS credentials, model access, region")
            print("   See: docs/04-AWS-BEDROCK.md")
            print()
            return False
            
    except Exception as e:
        print_check(f"AWS Bedrock error: {str(e)}", False)
        print()
        return False

def check_mongodb_indexes():
    """Check if MongoDB search indexes exist"""
    print("4. Checking MongoDB Search Indexes...")
    print()
    
    try:
        from database.mongodb import client
        import config
        
        db = client.get_database("ai_memory")
        
        # Check conversations collection
        if "conversations" in db.list_collection_names():
            conversations = db.get_collection("conversations")
            
            # Note: Can't directly list search indexes via pymongo easily
            # This is a basic check that collection exists
            count = conversations.count_documents({})
            print(f"   Conversations collection: {count} documents")
            
            print("⚠️  Search indexes cannot be verified programmatically")
            print("   Please verify in MongoDB Atlas UI:")
            print(f"   - {config.CONVERSATIONS_VECTOR_SEARCH_INDEX_NAME}")
            print(f"   - {config.CONVERSATIONS_FULLTEXT_SEARCH_INDEX_NAME}")
        else:
            print("⚠️  Conversations collection not yet created")
            print("   Will be created when first message is sent")
        
        print()
        
        # Check memory_nodes collection
        if "memory_nodes" in db.list_collection_names():
            memory_nodes = db.get_collection("memory_nodes")
            count = memory_nodes.count_documents({})
            print(f"   Memory nodes collection: {count} documents")
            
            print("⚠️  Memory vector index cannot be verified programmatically")
            print("   Please verify in MongoDB Atlas UI:")
            print(f"   - {config.MEMORY_NODES_VECTOR_SEARCH_INDEX_NAME}")
        else:
            print("⚠️  Memory nodes collection not yet created")
            print("   Will be created when first memory is stored")
        
        print()
        print("📖 Index creation guide: docs/03-MONGODB-ATLAS.md")
        print()
        
        return True
        
    except Exception as e:
        print_check(f"Index check error: {str(e)}", False)
        print()
        return False

def check_python_packages():
    """Check if required Python packages are installed"""
    print("5. Checking Python dependencies...")
    print()
    
    required_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pymongo", "MongoDB driver"),
        ("boto3", "AWS SDK"),
        ("pydantic", "Data validation"),
        ("python-dotenv", "Environment loader"),
    ]
    
    all_installed = True
    for package, description in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_check(f"{package}: Installed", True)
        except ImportError:
            print_check(f"{package}: Missing ({description})", False)
            all_installed = False
    
    print()
    
    if not all_installed:
        print("Install missing packages:")
        print("  pip3 install -r requirements.txt")
        print()
    
    return all_installed

def check_frontend():
    """Check frontend setup"""
    print("6. Checking frontend setup...")
    print()
    
    frontend_dir = project_root / "figmaUI"
    
    # Check directory exists
    if not frontend_dir.exists():
        print_check("figmaUI directory: Missing", False)
        print()
        return False
    
    print_check("figmaUI directory: Found", True)
    
    # Check node_modules
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print_check("node_modules: Installed", True)
    else:
        print_check("node_modules: Not installed", False)
        print("   Run: cd figmaUI && npm install")
    
    # Check .env.local
    env_local = frontend_dir / ".env.local"
    if env_local.exists():
        print_check(".env.local: Exists", True)
        
        # Check API URL
        with open(env_local) as f:
            content = f.read()
            if "VITE_API_BASE_URL" in content:
                print("   API URL configured")
    else:
        print("⚠️  .env.local: Not found (will use defaults)")
    
    print()
    return True

def main():
    """Main validation function"""
    print_header("AI Memory Service - Setup Validation")
    
    print("Validating your setup...")
    print("This will check:")
    print("  • Environment variables")
    print("  • MongoDB Atlas connection")
    print("  • AWS Bedrock access")
    print("  • MongoDB Search Indexes")
    print("  • Python dependencies")
    print("  • Frontend configuration")
    
    results = {}
    
    # Run all checks
    results['env'] = check_environment_variables()
    results['python'] = check_python_packages()
    results['mongodb'] = check_mongodb_connection()
    results['bedrock'] = check_aws_bedrock()
    results['indexes'] = check_mongodb_indexes()
    results['frontend'] = check_frontend()
    
    # Summary
    print_header("Validation Summary")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("✅ All checks passed!")
        print()
        print("Your setup is complete and ready to use.")
        print()
        print("Next steps:")
        print("  1. Start the application:")
        print("     ./scripts/start_demo.sh")
        print()
        print("  2. Open your browser:")
        print("     http://localhost:5173")
        print()
        print("  3. Try the demo features!")
        print()
        return 0
    else:
        print("⚠️  Some checks failed")
        print()
        print("Review the errors above and:")
        print()
        
        if not results['env']:
            print("  • Add missing environment variables to .env")
            print("    See: docs/02-SETUP-GUIDE.md")
        
        if not results['python']:
            print("  • Install Python dependencies:")
            print("    pip3 install -r requirements.txt")
        
        if not results['mongodb']:
            print("  • Fix MongoDB connection:")
            print("    See: docs/03-MONGODB-ATLAS.md")
        
        if not results['bedrock']:
            print("  • Configure AWS Bedrock access:")
            print("    See: docs/04-AWS-BEDROCK.md")
        
        if not results['frontend']:
            print("  • Install frontend dependencies:")
            print("    cd figmaUI && npm install")
        
        print()
        print("Then run this script again to verify.")
        print()
        print("Need help? See: docs/05-TROUBLESHOOTING.md")
        print()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation error: {e}")
        print("\nPlease ensure you're in the project root directory")
        print("and that .env file exists with valid configuration")
        sys.exit(1)
