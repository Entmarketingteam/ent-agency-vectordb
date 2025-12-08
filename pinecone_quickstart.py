#!/usr/bin/env python3
"""
Pinecone Quick Start - Following Best Practices from AGENTS.md
This script helps you get started with Pinecone using the latest patterns
"""

import os
import sys
from pathlib import Path

# Check for API key
api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    print("⚠️  PINECONE_API_KEY not found in environment")
    print("\nPlease set it using one of these methods:")
    print("1. PowerShell: $env:PINECONE_API_KEY = 'your-key'")
    print("2. Create .env file with: PINECONE_API_KEY=your-key")
    print("3. Windows: set PINECONE_API_KEY=your-key")
    sys.exit(1)

print("="*70)
print("  Pinecone Quick Start")
print("="*70)
print()

# Try to import pinecone
try:
    from pinecone import Pinecone
    print("✓ Pinecone SDK installed")
except ImportError:
    print("Installing Pinecone SDK...")
    import subprocess
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "pinecone", "--break-system-packages"
    ])
    from pinecone import Pinecone
    print("✓ Pinecone SDK installed")

# Initialize client
try:
    pc = Pinecone(api_key=api_key)
    print("✓ Connected to Pinecone")
except Exception as e:
    print(f"✗ Failed to connect: {e}")
    sys.exit(1)

print()
print("Choose an option:")
print("1. Quick Test - Create index, upsert data, and search")
print("2. Check existing indexes")
print("3. Create new index with integrated embeddings")
print()

choice = input("Enter choice (1-3): ").strip()

if choice == "1":
    print("\n" + "="*70)
    print("  Quick Test")
    print("="*70)
    
    index_name = "agentic-quickstart-test"
    
    # Check if index exists
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    if index_name in existing_indexes:
        print(f"✓ Index '{index_name}' already exists")
        index = pc.Index(index_name)
    else:
        print(f"\n⚠️  Index '{index_name}' not found.")
        print("According to best practices, indexes should be created with the CLI:")
        print(f"  pc index create -n {index_name} -m cosine -c aws -r us-east-1 \\")
        print("    --model llama-text-embed-v2 --field_map text=content")
        print("\nFor now, we'll check what indexes you have...")
        if existing_indexes:
            print(f"\nExisting indexes: {', '.join(existing_indexes)}")
        else:
            print("\nNo indexes found. Please create one using the CLI first.")
        sys.exit(0)
    
    # Sample data
    print("\nPreparing sample data...")
    records = [
        {"_id": "rec1", "content": "The Eiffel Tower was completed in 1889 and stands in Paris, France.", "category": "history"},
        {"_id": "rec2", "content": "Photosynthesis allows plants to convert sunlight into energy.", "category": "science"},
        {"_id": "rec3", "content": "Shakespeare wrote many famous plays, including Hamlet and Macbeth.", "category": "literature"},
        {"_id": "rec4", "content": "The Great Wall of China was built to protect against invasions.", "category": "history"},
        {"_id": "rec5", "content": "Leonardo da Vinci painted the Mona Lisa.", "category": "art"},
    ]
    
    # Upsert data
    print("Upserting records to namespace 'test-namespace'...")
    try:
        index.upsert_records("test-namespace", records)
        print("✓ Records upserted successfully")
    except Exception as e:
        print(f"✗ Failed to upsert: {e}")
        sys.exit(1)
    
    # Wait for indexing
    print("\nWaiting for vectors to be indexed (10 seconds)...")
    import time
    time.sleep(10)
    
    # Search
    print("\nSearching for: 'Famous historical structures and monuments'")
    try:
        results = index.search(
            namespace="test-namespace",
            query={
                "top_k": 5,
                "inputs": {"text": "Famous historical structures and monuments"}
            },
            rerank={
                "model": "bge-reranker-v2-m3",
                "top_n": 5,
                "rank_fields": ["content"]
            }
        )
        
        print("\n" + "="*70)
        print("  Search Results")
        print("="*70)
        for hit in results['result']['hits']:
            print(f"\nID: {hit['_id']}")
            print(f"Score: {round(hit['_score'], 3)}")
            print(f"Category: {hit['fields'].get('category', 'N/A')}")
            print(f"Content: {hit['fields'].get('content', 'N/A')[:80]}...")
        
        print("\n✓ Quick test completed successfully!")
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        import traceback
        traceback.print_exc()

elif choice == "2":
    print("\n" + "="*70)
    print("  Existing Indexes")
    print("="*70)
    
    indexes = list(pc.list_indexes())
    if indexes:
        print(f"\nFound {len(indexes)} index(es):\n")
        for idx in indexes:
            print(f"  • {idx.name}")
            try:
                index = pc.Index(idx.name)
                stats = index.describe_index_stats()
                print(f"    Total vectors: {stats.total_vector_count}")
                if hasattr(stats, 'namespaces') and stats.namespaces:
                    print(f"    Namespaces: {', '.join(stats.namespaces.keys())}")
            except Exception as e:
                print(f"    (Could not get stats: {e})")
            print()
    else:
        print("\nNo indexes found.")
        print("\nTo create an index, use the Pinecone CLI:")
        print("  pc index create -n my-index -m cosine -c aws -r us-east-1 \\")
        print("    --model llama-text-embed-v2 --field_map text=content")

elif choice == "3":
    print("\n" + "="*70)
    print("  Create Index")
    print("="*70)
    print("\n⚠️  According to best practices, indexes should be created with the CLI.")
    print("\nUse this command:")
    print("  pc index create -n <index-name> -m cosine -c aws -r us-east-1 \\")
    print("    --model llama-text-embed-v2 --field_map text=content")
    print("\nFor Windows, download the CLI from:")
    print("  https://github.com/pinecone-io/cli/releases")
    print("\nOr install via winget (if available):")
    print("  winget install Pinecone.CLI")

else:
    print("Invalid choice")

print("\n" + "="*70)
print("  Next Steps")
print("="*70)
print("\n1. Install Pinecone CLI for index management:")
print("   https://github.com/pinecone-io/cli/releases")
print("\n2. Create indexes using CLI (not SDK)")
print("\n3. Use SDK for data operations (upsert, search, delete)")
print("\n4. Always use namespaces for data isolation")
print("\n5. Always use reranking for better search results")
print("\nSee AGENTS.md for complete best practices guide.")
print("="*70)


