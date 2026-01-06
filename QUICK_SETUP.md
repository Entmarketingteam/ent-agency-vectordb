# 🚀 Quick Setup Guide

Your API keys have been configured! Follow these steps to get started.

## Step 1: Install Dependencies

You may need to install packages. Try one of these methods:

### Option A: Install from requirements.txt
```powershell
pip install -r requirements.txt --break-system-packages
```

### Option B: Install individually (if network issues)
```powershell
pip install pinecone --break-system-packages
pip install openai --break-system-packages
pip install python-dotenv --break-system-packages
```

### Option C: If you have network/proxy issues
You may need to:
1. Configure pip to use a proxy
2. Or install packages manually
3. Or use a different network connection

## Step 2: Set Environment Variables

### Option A: Use the PowerShell script (Easiest)
```powershell
.\setup_env.ps1
```

### Option B: Set manually in PowerShell
```powershell
$env:PINECONE_API_KEY='your-pinecone-api-key'
$env:OPENAI_API_KEY='your-openai-api-key'
```

### Option C: Create .env file (Recommended for persistence)
Copy the example file and fill in your keys:
```powershell
copy .env.example .env
# Then edit .env with your actual API keys
```

Or create `.env` manually with:
```
PINECONE_API_KEY=your-pinecone-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here
```

**Note:** The code will automatically load from `.env` file if `python-dotenv` is installed.

## Step 3: Test Your Setup

```powershell
python test_setup.py
```

This should show:
- ✓ All packages installed
- ✓ API keys are set
- ✓ Can connect to Pinecone
- ✓ Can connect to OpenAI

## Step 4: Create/Verify Pinecone Index

### Option A: Using CLI (Recommended - Best Performance)

First, install Pinecone CLI:
- Download from: https://github.com/pinecone-io/cli/releases
- Or use: `winget install Pinecone.CLI`

Then create index:
```powershell
# Authenticate
pc auth configure --api-key $env:PINECONE_API_KEY

# Create index with integrated embeddings
pc index create -n ent-agency-campaigns -m cosine -c aws -r us-east-1 --model llama-text-embed-v2 --field_map text=content
```

### Option B: Verify Existing Index

```powershell
python pinecone_setup.py
```

This will:
- Check if index exists
- Connect to it
- Offer to create if missing

## Step 5: Ingest Your Data

### If Using Google Sheets:

1. Make sure you have `credentials.json` file (Google service account)
2. Update spreadsheet ID in `data_ingestion.py` or `config.json`
3. Run:
```powershell
python data_ingestion.py
```

### If You Have Data Ready:

You can use the Python API directly - see `NEXT_STEPS.md` for examples.

## Step 6: Query Your Data

```powershell
python query_interface.py
```

Choose option 1 for interactive search, then try queries like:
- "What were our best campaigns in Q4?"
- "Show me all Thorne campaigns"
- "Find high engagement Instagram posts"

## Troubleshooting

### Network/Proxy Issues Installing Packages

If you're behind a corporate firewall:
1. Configure pip proxy: `pip install --proxy http://proxy:port package`
2. Or download packages manually
3. Or use a different network

### API Keys Not Working

1. Verify keys are set: `echo $env:PINECONE_API_KEY`
2. Make sure no extra spaces in keys
3. Check keys are valid in Pinecone/OpenAI dashboards

### Index Creation Fails

1. Make sure you're authenticated: `pc auth configure --api-key $env:PINECONE_API_KEY`
2. Check your Pinecone plan allows index creation
3. Try creating via Pinecone dashboard first

## Next Steps

Once everything is working:
- See `NEXT_STEPS.md` for detailed workflow
- See `UPDATES.md` for what's new
- See `README.md` for full documentation

## Security Best Practices

✅ **API keys are stored in `.env` file** (not committed to git)
✅ **`.env` is in `.gitignore`** (will never be pushed)
✅ **`.env.example` is a template** (safe to commit, no real keys)

**Important:** Never commit your `.env` file or put API keys in code files!

