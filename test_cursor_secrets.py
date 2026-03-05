"""
Test script to verify Cursor Global Secrets are configured correctly.
Run this after setting up secrets in Cursor → Settings → Secrets
"""
import os
import sys

def test_secrets():
    """Test that Cursor secrets are available"""
    print("🔍 Checking Cursor Global Secrets...\n")
    print("=" * 60)
    
    secrets = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY")
    }
    
    results = {}
    for key, value in secrets.items():
        if value:
            # Show first 8 chars and last 4 chars for verification
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"✅ {key:30} {masked:20} (configured)")
            results[key] = True
        else:
            print(f"❌ {key:30} {'NOT FOUND':20}")
            results[key] = False
    
    print("=" * 60)
    
    # Summary
    configured = sum(results.values())
    total = len(results)
    
    print(f"\n📊 Summary: {configured}/{total} secrets configured")
    
    if all(results.values()):
        print("\n🎉 All secrets configured! Cursor is ready to use.")
        print("\n💡 You can now:")
        print("   - Use OpenAI, Supabase, and Pinecone in any project")
        print("   - Access MCP tools in Cursor Chat")
        print("   - Skip .env files - secrets are global!")
        return True
    else:
        print("\n⚠️  Some secrets are missing.")
        print("\n📝 To fix:")
        print("   1. Open Cursor → Settings → Secrets")
        print("   2. Click 'Add Secret' for each missing key")
        print("   3. Restart Cursor")
        print("   4. Run this script again")
        return False

def test_mcp_config():
    """Check if MCP config file exists"""
    import pathlib
    mcp_config_path = pathlib.Path.home() / ".cursor" / "mcp" / "config.json"
    
    print("\n🔧 Checking MCP Configuration...")
    if mcp_config_path.exists():
        print(f"✅ MCP config found at: {mcp_config_path}")
        try:
            import json
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
            servers = list(config.get("mcpServers", {}).keys())
            print(f"   Configured servers: {', '.join(servers)}")
            return True
        except Exception as e:
            print(f"⚠️  MCP config exists but has errors: {e}")
            return False
    else:
        print(f"❌ MCP config not found at: {mcp_config_path}")
        print("   (This is OK if you only want to use secrets, not MCP tools)")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CURSOR GLOBAL SECRETS & MCP SETUP VERIFICATION")
    print("=" * 60 + "\n")
    
    secrets_ok = test_secrets()
    mcp_ok = test_mcp_config()
    
    print("\n" + "=" * 60)
    if secrets_ok:
        print("✅ Setup complete! You're ready to use Cursor secrets.")
    else:
        print("⚠️  Please configure missing secrets in Cursor Settings.")
    print("=" * 60 + "\n")
    
    sys.exit(0 if secrets_ok else 1)








