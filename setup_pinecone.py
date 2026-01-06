#!/usr/bin/env python3
"""
Quick setup script for Pinecone Vector Database
This script will help you set up and verify your Pinecone index
"""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("OK Loaded environment variables from .env file")
except ImportError:
    # Try to manually load .env file
    if os.path.exists('.env'):
        print("Loading .env file manually...")
        try:
            with open('.env', 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value:
                                os.environ[key] = value
                                # Debug: print first few keys loaded
                                if key == 'PINECONE_API_KEY' or key == 'OPENAI_API_KEY':
                                    print(f"  Loaded {key}: {value[:15]}...")
            print("OK Loaded .env file manually")
        except Exception as e:
            print(f"WARN Could not load .env: {e}")
    else:
        print("WARN python-dotenv not installed and .env not found")
except Exception as e:
    print(f"WARN Could not load .env: {e}")

# Check API keys
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not PINECONE_API_KEY:
    print("\nERROR: PINECONE_API_KEY not found!")
    print("   Make sure you have a .env file with your API keys")
    print("   Or set it as: $env:PINECONE_API_KEY='your-key'")
    sys.exit(1)

if not OPENAI_API_KEY:
    print("\nERROR: OPENAI_API_KEY not found!")
    print("   Make sure you have a .env file with your API keys")
    print("   Or set it as: $env:OPENAI_API_KEY='your-key'")
    sys.exit(1)

print(f"OK PINECONE_API_KEY found ({PINECONE_API_KEY[:10]}...)")
print(f"OK OPENAI_API_KEY found ({OPENAI_API_KEY[:10]}...)")

# Try to import Pinecone
try:
    from pinecone import Pinecone
    print("OK Pinecone SDK installed")
except ImportError:
    print("\nERROR Pinecone SDK not installed!")
    print("\nPlease install it:")
    print("  pip install pinecone --break-system-packages")
    print("\nIf you have network issues, you may need to:")
    print("  1. Configure pip proxy")
    print("  2. Use a different network")
    print("  3. Install packages manually")
    sys.exit(1)

# Try to import OpenAI
try:
    import openai
    print("OK OpenAI SDK installed")
except ImportError:
    print("\nWARN OpenAI SDK not installed (optional for some operations)")
    print("  pip install openai --break-system-packages")

# Initialize Pinecone
print("\n" + "="*70)
print("Connecting to Pinecone...")
print("="*70)

try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    indexes = list(pc.list_indexes())
    print(f"OK Connected to Pinecone successfully!")
    print(f"  Found {len(indexes)} existing index(es)")
    
    if indexes:
        print("\nExisting indexes:")
        for idx in indexes:
            print(f"  • {idx.name}")
    
    # Check for our index
    index_name = "ent-agency-campaigns"
    index_names = [idx.name for idx in indexes]
    
    if index_name in index_names:
        print(f"\nOK Index '{index_name}' already exists!")
        print("\nYou can now:")
        print("  1. Ingest data: python data_ingestion.py")
        print("  2. Query data: python query_interface.py")
    else:
        print(f"\n⚠️  Index '{index_name}' not found")
        print("\n" + "="*70)
        print("CREATE INDEX OPTIONS")
        print("="*70)
        print("\nOption 1: Using Pinecone CLI (Recommended - Best Performance)")
        print("  Install CLI: https://github.com/pinecone-io/cli/releases")
        print("  Then run:")
        print(f"    pc auth configure --api-key $env:PINECONE_API_KEY")
        print(f"    pc index create -n {index_name} -m cosine -c aws -r us-east-1 \\")
        print("      --model llama-text-embed-v2 --field_map text=content")
        print("\n  Benefits:")
        print("    - Integrated embeddings (faster, cheaper)")
        print("    - Better performance")
        print("    - Latest Pinecone best practices")
        
        print("\nOption 2: Create programmatically (Basic index)")
        print("  This creates a basic index without integrated embeddings")
        print("  Run: python pinecone_setup.py")
        print("\n  Note: Less optimal, but works if CLI isn't available")
        
        choice = input("\nWould you like to create the index programmatically now? (y/n): ").strip().lower()
        
        if choice == 'y':
            print("\nCreating index...")
            from pinecone import ServerlessSpec
            try:
                pc.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"OK Index '{index_name}' created successfully!")
                print("\nWARN: This is a basic index without integrated embeddings.")
                print("   For better performance, recreate with CLI using integrated embeddings.")
            except Exception as e:
                print(f"ERROR: Failed to create index: {e}")
                print("\nYou may need to:")
                print("  1. Check your Pinecone plan allows index creation")
                print("  2. Use the CLI method instead")
        else:
            print("\nSkipping index creation. Use CLI method for best results.")
    
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. If index was created, wait ~30 seconds for it to initialize")
    print("  2. Ingest your data: python data_ingestion.py")
    print("  3. Query your data: python query_interface.py")
    print()
    
except Exception as e:
    print(f"\nERROR: Error connecting to Pinecone: {e}")
    print("\nTroubleshooting:")
    print("  1. Verify your API key is correct")
    print("  2. Check your internet connection")
    print("  3. Check Pinecone service status")
    sys.exit(1)

