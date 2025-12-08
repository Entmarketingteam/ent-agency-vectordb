"""
Test Script for ENT Agency Vector Database
Run this to verify your setup is working correctly
"""

import os
import sys


def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    
    try:
        import pinecone
        print("✓ pinecone")
    except ImportError:
        print("✗ pinecone - Run: pip install pinecone")
        return False
    
    try:
        import openai
        print("✓ openai")
    except ImportError:
        print("✗ openai - Run: pip install openai")
        return False
    
    try:
        import gspread
        print("✓ gspread")
    except ImportError:
        print("✗ gspread - Run: pip install gspread")
        return False
    
    try:
        from oauth2client.service_account import ServiceAccountCredentials
        print("✓ oauth2client")
    except ImportError:
        print("✗ oauth2client - Run: pip install oauth2client")
        return False
    
    return True


def test_env_vars():
    """Test if environment variables are set"""
    print("\nTesting environment variables...")
    
    pinecone_key = os.getenv('PINECONE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if pinecone_key:
        print(f"✓ PINECONE_API_KEY is set ({pinecone_key[:8]}...)")
    else:
        print("✗ PINECONE_API_KEY is not set")
    
    if openai_key:
        print(f"✓ OPENAI_API_KEY is set ({openai_key[:8]}...)")
    else:
        print("✗ OPENAI_API_KEY is not set")
    
    return bool(pinecone_key and openai_key)


def test_credentials():
    """Test if Google credentials exist"""
    print("\nTesting Google credentials...")
    
    if os.path.exists('credentials.json'):
        print("✓ credentials.json found")
        return True
    else:
        print("✗ credentials.json not found")
        return False


def test_pinecone_connection():
    """Test Pinecone connection"""
    print("\nTesting Pinecone connection...")
    
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            print("✗ Cannot test - PINECONE_API_KEY not set")
            return False
        
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        
        print(f"✓ Connected to Pinecone")
        print(f"  Found {len(indexes)} index(es)")
        
        # Check for our specific index
        index_names = [idx.name for idx in indexes]
        if 'ent-agency-campaigns' in index_names:
            print("  ✓ 'ent-agency-campaigns' index exists")
        else:
            print("  ⚠ 'ent-agency-campaigns' index not found (run pinecone_setup.py)")
        
        return True
        
    except Exception as e:
        print(f"✗ Pinecone connection failed: {e}")
        return False


def test_openai_connection():
    """Test OpenAI connection"""
    print("\nTesting OpenAI connection...")
    
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("✗ Cannot test - OPENAI_API_KEY not set")
            return False
        
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple embedding
        response = client.embeddings.create(
            input="test",
            model="text-embedding-3-small"
        )
        
        print(f"✓ Connected to OpenAI")
        print(f"  Embedding dimension: {len(response.data[0].embedding)}")
        
        return True
        
    except Exception as e:
        print(f"✗ OpenAI connection failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("  ENT Agency Vector Database - System Test")
    print("="*70 + "\n")
    
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['env_vars'] = test_env_vars()
    results['credentials'] = test_credentials()
    results['pinecone'] = test_pinecone_connection()
    results['openai'] = test_openai_connection()
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70 + "\n")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    
    if all_passed:
        print("🎉 All tests passed! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Run: python data_ingestion.py")
        print("2. Run: python query_interface.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip install -r requirements.txt --break-system-packages")
        print("- Set API keys: export PINECONE_API_KEY='...' OPENAI_API_KEY='...'")
        print("- Add Google credentials: Save as credentials.json")
    
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
