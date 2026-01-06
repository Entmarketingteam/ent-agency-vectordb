# 🚀 Next Steps - Action Plan

Follow these steps to get your updated vector database running with the latest Pinecone patterns.

## Step 1: Verify Your Setup ✅

First, make sure everything is configured:

```bash
python test_setup.py
```

**What to check:**
- ✓ All packages installed
- ✓ PINECONE_API_KEY is set
- ✓ OPENAI_API_KEY is set
- ✓ Google credentials.json exists (if using Google Sheets)
- ✓ Can connect to Pinecone
- ✓ Can connect to OpenAI

**If anything fails:**
- Install packages: `pip install -r requirements.txt --break-system-packages`
- Set API keys (PowerShell): 
  ```powershell
  $env:PINECONE_API_KEY='your-key'
  $env:OPENAI_API_KEY='your-key'
  ```

---

## Step 2: Create/Verify Your Pinecone Index 🗄️

### Option A: Create with CLI (Recommended - Best Performance) ⭐

This creates an index with integrated embeddings for better performance:

```bash
# Install Pinecone CLI first (if not installed)
# Windows: Download from https://github.com/pinecone-io/cli/releases
# Or use: winget install Pinecone.CLI

# Authenticate
pc auth configure --api-key $env:PINECONE_API_KEY

# Create index with integrated embeddings
pc index create -n ent-agency-campaigns -m cosine -c aws -r us-east-1 --model llama-text-embed-v2 --field_map text=content
```

**Benefits:**
- ✅ Faster embeddings (no OpenAI calls needed)
- ✅ Better performance
- ✅ Lower costs
- ✅ Latest Pinecone best practices

### Option B: Verify Existing Index

If you already have an index:

```bash
python pinecone_setup.py
```

This will:
- Check if index exists
- Connect to it
- Show you if it needs to be recreated

**Note:** If your existing index doesn't have integrated embeddings, you can:
1. Keep using it (will fall back to OpenAI embeddings)
2. Or recreate it with Option A for better performance

---

## Step 3: Ingest Your Data 📥

### If Using Google Sheets:

1. **Update your spreadsheet ID** in `data_ingestion.py` (line ~272) or use `config.json`

2. **Run ingestion:**
   ```bash
   python data_ingestion.py
   ```

3. **What happens:**
   - Connects to Google Sheets
   - Extracts campaign data
   - Transforms to proper format
   - Stores in Pinecone with namespaces (by quarter)
   - Shows progress and stats

### If You Have Data in Another Format:

You can use the `ENTAgencyVectorDB` class directly:

```python
from pinecone_setup import ENTAgencyVectorDB
import os

db = ENTAgencyVectorDB(
    pinecone_api_key=os.getenv('PINECONE_API_KEY'),
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
db.create_index()

# Your campaign data
campaigns = [
    {
        'quarter': '2024 Q4',
        'creator': 'Nicki Entenmann',
        'brand': 'Thorne',
        'campaign_type': 'Instagram Reel',
        'platform': 'Instagram',
        'date': '2024-10-15',
        'metrics': {
            'impressions': 125000,
            'engagement': 8500
        },
        'revenue': 2500.00,
        'content_description': 'Product review video'
    },
    # ... more campaigns
]

# Ingest with namespace (auto-determined from quarter)
db.ingest_bulk_campaigns(campaigns, namespace="2024_q4")
```

---

## Step 4: Test Your Queries 🔍

### Interactive Mode (Recommended for First Test):

```bash
python query_interface.py
```

Then choose option **1** for interactive search mode.

**Try these test queries:**
- "What were our best performing campaigns in Q4?"
- "Show me all Thorne campaigns"
- "Find high engagement Instagram reels"
- "What campaigns did Nicki Entenmann create?"

### Programmatic Queries:

```python
from query_interface import CampaignQueryInterface
import os

interface = CampaignQueryInterface(
    pinecone_api_key=os.getenv('PINECONE_API_KEY'),
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

# Natural language search
results = interface.search("high engagement campaigns", top_k=10)

# Search by brand
interface.query_by_brand("Thorne", top_k=10)

# Search by creator
interface.query_by_creator("Nicki Entenmann", top_k=10)

# Best performing campaigns
interface.query_best_performing(metric="engagement", quarter="2024 Q4")
```

---

## Step 5: Verify Everything Works ✅

### Check Index Stats:

```python
from pinecone_setup import ENTAgencyVectorDB
import os

db = ENTAgencyVectorDB(
    pinecone_api_key=os.getenv('PINECONE_API_KEY'),
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
db.create_index()

# Get overall stats
stats = db.get_stats()
print(f"Total vectors: {stats.total_vector_count}")

# Get namespace-specific stats
namespace_stats = db.get_stats(namespace="2024_q4")
print(f"Vectors in 2024 Q4: {namespace_stats}")
```

### Verify Search Quality:

1. **Test relevance:** Do results match your queries?
2. **Test speed:** Queries should return in 1-3 seconds
3. **Test filters:** Try filtering by quarter, creator, brand
4. **Test reranking:** Compare results with/without reranking (should be better with)

---

## Step 6: Set Up Automation (Optional) 🔄

### For Regular Updates:

```bash
# Update from config.json
python auto_update.py

# Update specific sheet
python auto_update.py <spreadsheet_id>

# Update current quarter only
python auto_update.py --current
```

### Schedule Regular Updates:

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/weekly)
4. Action: Run `python auto_update.py`

**Linux/Mac Cron:**
```bash
# Edit crontab
crontab -e

# Add line (runs daily at 2 AM)
0 2 * * * cd /path/to/project && python auto_update.py
```

---

## Troubleshooting 🔧

### Issue: "Index not found"
**Solution:** Create index first (Step 2)

### Issue: "No results found"
**Solutions:**
- Check if data was ingested: `db.get_stats()`
- Try broader queries first
- Check namespace matches (e.g., "2024_q4" not "2024 Q4")
- Wait a few seconds after ingestion (indexing takes time)

### Issue: "Field map error" or "Content field not found"
**Solution:** Your index needs integrated embeddings. Recreate with CLI:
```bash
pc index create -n ent-agency-campaigns -m cosine -c aws -r us-east-1 --model llama-text-embed-v2 --field_map text=content
```

### Issue: "Rate limit errors"
**Solutions:**
- Reduce batch size in `ingest_bulk_campaigns()` (default: 96)
- Add delays between batches
- Check your Pinecone plan limits

### Issue: "Authentication failed" (Google Sheets)
**Solutions:**
- Verify `credentials.json` exists
- Check service account email has access to sheet
- Re-authenticate: Delete `token.json` and run again

---

## Quick Reference Commands 📋

```bash
# Test setup
python test_setup.py

# Create/verify index
python pinecone_setup.py

# Ingest data
python data_ingestion.py

# Query data
python query_interface.py

# Auto update
python auto_update.py

# Quick start wizard
python quick_start.py
```

---

## What's New in This Update? 🆕

1. **Namespaces:** Data organized by quarter automatically
2. **Reranking:** Better search results (enabled by default)
3. **Integrated Embeddings:** Ready for llama-text-embed-v2 (via CLI)
4. **New APIs:** Using `upsert_records()` and `search()` instead of old methods
5. **Backward Compatible:** Old code still works

See `UPDATES.md` for complete details.

---

## Success Checklist ✅

- [ ] Setup verified (`test_setup.py` passes)
- [ ] Index created/verified
- [ ] Data ingested successfully
- [ ] Queries return relevant results
- [ ] Search is fast (1-3 seconds)
- [ ] Filters work correctly
- [ ] Ready for production use!

---

## Need Help? 💬

- Check `README.md` for feature documentation
- See `UPDATES.md` for API changes
- Review `SETUP_CHECKLIST.md` for detailed setup
- Run `python test_setup.py` for diagnostics

**You're all set! Start with Step 1 and work through each step.** 🚀


