# 🚀 Cursor MCP & Global Secrets Setup Guide

This guide will help you configure Cursor to automatically have OpenAI, Supabase, and Pinecone connections available across **all your projects** without needing to set up environment variables each time.

## ✅ Two-Layer Setup

### Layer 1: Cursor Global Secrets (Required)

**Step 1: Open Cursor Settings**
- Press `Ctrl+,` (or `Cmd+,` on Mac) to open Settings
- Or go to: **Cursor → Settings → Secrets**

**Step 2: Add Your API Keys**

Click "Add Secret" for each of these:

| Secret Name | Description | Where to Get It |
|------------|-------------|-----------------|
| `OPENAI_API_KEY` | Your OpenAI API key | https://platform.openai.com/api-keys |
| `SUPABASE_URL` | Your Supabase project URL | https://app.supabase.com → Project Settings → API |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Same as above |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Same as above (⚠️ Keep secret!) |
| `PINECONE_API_KEY` | Your Pinecone API key | https://app.pinecone.io → API Keys |

**Step 3: Verify Secrets**
- All secrets should show as "✓ Configured" in Cursor Settings
- These are now available globally to all projects

### Layer 2: MCP (Model Context Protocol) Configuration

**✅ Already Configured!**

I've created your MCP config at:
```
C:\Users\ethan.atchley\.cursor\mcp\config.json
```

This includes:
- ✅ **OpenAI MCP Server** - Direct access to GPT-4, embeddings, Assistants API
- ✅ **Supabase MCP Server** - SQL queries, table management, auth, storage
- ✅ **Filesystem MCP** - File operations across your system
- ✅ **Fetch MCP** - HTTP requests and API calls

**What This Gives You:**

1. **In Cursor Chat/Composer:**
   - Ask: "Query my Supabase users table"
   - Ask: "Generate embeddings using OpenAI"
   - Ask: "Create a new table in Supabase"
   - Cursor can execute these directly!

2. **In Your Code:**
   ```python
   import os
   
   # These automatically resolve from Cursor Secrets
   openai_key = os.getenv("OPENAI_API_KEY")
   supabase_url = os.getenv("SUPABASE_URL")
   pinecone_key = os.getenv("PINECONE_API_KEY")
   ```

3. **No More .env Files Needed:**
   - Cursor injects secrets automatically
   - Works across all projects
   - Never committed to Git

## 🔧 Installing MCP Server Dependencies

The MCP servers use `npx` which comes with Node.js. If you don't have Node.js:

**Windows (using Chocolatey):**
```powershell
choco install nodejs
```

**Or download from:**
https://nodejs.org/

**Verify installation:**
```powershell
node --version
npm --version
```

The `-y` flag in the config means MCP servers will auto-install on first use, so you don't need to install anything manually!

## 🎯 How to Use

### Example 1: Using in Cursor Chat

Just ask naturally:
- "Query my Supabase database for all users created this month"
- "Generate embeddings for this text using OpenAI"
- "Create a new Pinecone index called 'my-index'"

Cursor will use the MCP tools automatically!

### Example 2: Using in Your Code

```python
import os
from pinecone import Pinecone
from openai import OpenAI
from supabase import create_client

# All these automatically get values from Cursor Secrets
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)
```

### Example 3: Testing Your Setup

Create a test file:

```python
# test_cursor_secrets.py
import os

def test_secrets():
    """Test that Cursor secrets are available"""
    secrets = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY")
    }
    
    print("🔍 Checking Cursor Secrets...\n")
    for key, value in secrets.items():
        if value:
            print(f"✅ {key}: {'*' * 20} (configured)")
        else:
            print(f"❌ {key}: NOT FOUND")
    
    if all(secrets.values()):
        print("\n🎉 All secrets configured! Cursor is ready.")
    else:
        print("\n⚠️  Some secrets missing. Add them in Cursor → Settings → Secrets")

if __name__ == "__main__":
    test_secrets()
```

Run it:
```bash
python test_cursor_secrets.py
```

## 🔒 Security Notes

1. **Secrets are stored locally** - Never synced to cloud (unless you enable Cursor Settings sync)
2. **MCP config references secrets** - Uses `${secrets.KEY_NAME}` syntax
3. **Never commit secrets** - They're separate from your code
4. **Service Role Key** - Supabase service role key has admin access, keep it secure!

## 🛠️ Troubleshooting

### MCP servers not working?
1. Check Node.js is installed: `node --version`
2. Restart Cursor after adding secrets
3. Check MCP config path: `%USERPROFILE%\.cursor\mcp\config.json`

### Secrets not available in code?
1. Make sure you added them in **Cursor → Settings → Secrets** (not just environment variables)
2. Restart Cursor
3. Check secret names match exactly (case-sensitive)

### Want to add more MCP servers?

Edit `%USERPROFILE%\.cursor\mcp\config.json` and add:

```json
"puppeteer": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
  "env": {}
}
```

Popular MCP servers:
- `@modelcontextprotocol/server-github` - GitHub API
- `@modelcontextprotocol/server-postgres` - PostgreSQL
- `@modelcontextprotocol/server-brave-search` - Web search
- `@modelcontextprotocol/server-google-drive` - Google Drive

## 📚 Next Steps

1. ✅ Add all secrets in Cursor Settings
2. ✅ Verify Node.js is installed
3. ✅ Restart Cursor
4. ✅ Test with `test_cursor_secrets.py`
5. ✅ Start using MCP tools in Cursor Chat!

## 🎉 You're All Set!

Now every project automatically has access to:
- ✅ OpenAI (GPT-4, embeddings, Assistants)
- ✅ Supabase (SQL, auth, storage, realtime)
- ✅ Pinecone (vector search)
- ✅ Filesystem operations
- ✅ HTTP/Fetch capabilities

No more `.env` files, no more manual setup per project! 🚀







