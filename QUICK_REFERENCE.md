# ⚡ Quick Reference Guide

## 🚀 One-Command Setups

### First Time Setup
```bash
python quick_start.py
```

### Test Everything
```bash
python test_setup.py
```

### Create Database
```bash
python pinecone_setup.py
```

### Load Your Data
```bash
python data_ingestion.py
```

### Start Searching
```bash
python query_interface.py
```

### Auto Update
```bash
python auto_update.py
```

## 🔑 Environment Variables

```bash
export PINECONE_API_KEY='your-key'
export OPENAI_API_KEY='your-key'
```

Or create `.env` file:
```
PINECONE_API_KEY=your-key
OPENAI_API_KEY=your-key
```

## 📝 Common Queries

```
"What were our best campaigns in Q1 2024?"
"Show me all Thorne partnerships"
"Find high engagement Instagram reels"
"Compare Nicki vs Sara performance"
"What campaigns had over 100k impressions?"
"Top revenue generating posts last quarter"
```

## 🛠️ Quick Fixes

**API keys not working?**
```bash
echo $PINECONE_API_KEY  # Should show your key
```

**Google Sheets not connecting?**
```bash
ls credentials.json  # Should exist
```

**Index not found?**
```bash
python pinecone_setup.py  # Recreate it
```

**Need to start over?**
```bash
python quick_start.py  # Re-run wizard
```

## 📂 File Purposes

- `pinecone_setup.py` - Creates the database
- `data_ingestion.py` - Loads your campaign data
- `query_interface.py` - Search your campaigns
- `auto_update.py` - Automated data refresh
- `test_setup.py` - Verify everything works
- `quick_start.py` - Interactive setup wizard

## 🎯 What Each File Does

| File | Purpose | When to Use |
|------|---------|-------------|
| quick_start.py | Setup wizard | First time only |
| test_setup.py | Verify setup | Troubleshooting |
| pinecone_setup.py | Create database | Once at start |
| data_ingestion.py | Load data | After setup & updates |
| query_interface.py | Search | Daily use |
| auto_update.py | Auto refresh | Scheduled runs |

## 🔄 Typical Workflow

1. **First time**: `python quick_start.py`
2. **Daily**: `python query_interface.py`
3. **Weekly**: `python auto_update.py`
4. **Issues**: `python test_setup.py`

## 📊 Costs (Approximate)

- Pinecone: $0-70/month
- OpenAI: $1-10/month
- Google: Free
- **Total**: ~$1-80/month

## ⏱️ Time Investment

- Setup: 30 minutes
- First query: 5 minutes
- Daily use: Seconds
- Updates: Automated

## 🆘 Emergency Commands

```bash
# Everything broken? Start fresh
python quick_start.py

# Is it me or the APIs?
python test_setup.py

# Lost my data?
python data_ingestion.py

# Index corrupted?
python pinecone_setup.py
```

## 📞 Get Help

1. Run `python test_setup.py`
2. Check error messages
3. Review SETUP_CHECKLIST.md
4. Read relevant .md file

## 🎉 Success Indicators

✅ `test_setup.py` passes all tests
✅ Queries return results in <3 seconds
✅ Results are relevant to your query
✅ Can filter by quarter/creator/brand
✅ Auto updates work on schedule

---

**Keep this handy!** Pin it or print it.
