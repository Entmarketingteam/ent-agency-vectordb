# 🚀 Getting Started with ENT Agency Vector Database

Welcome! This system lets you search your influencer marketing campaigns using natural language. Ask questions like "What were our best Instagram campaigns last quarter?" and get instant, relevant results.

## Quick Start (5 minutes)

### 1️⃣ Get Your Keys

You need three things:

**Pinecone API Key** (for the database)
- Go to https://www.pinecone.io/ → Sign up → Get API key

**OpenAI API Key** (for search intelligence)
- Go to https://platform.openai.com/ → Sign up → Get API key

**Google Credentials** (for accessing your sheets)
- Go to https://console.cloud.google.com/ → Create project
- Enable Google Sheets API → Create Service Account
- Download credentials.json

### 2️⃣ Install

```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Set your API keys
export PINECONE_API_KEY='your-pinecone-key'
export OPENAI_API_KEY='your-openai-key'

# Place your credentials.json file in this folder
```

### 3️⃣ Setup

```bash
# Test everything works
python test_setup.py

# Create the database
python pinecone_setup.py

# Load your data (edit spreadsheet_id in the file first)
python data_ingestion.py
```

### 4️⃣ Search!

```bash
# Start searching
python query_interface.py
```

Then try queries like:
- "What were our best performing campaigns in Q1?"
- "Show me all Thorne campaigns"
- "Find high engagement Instagram reels"
- "Compare Nicki vs Sara's performance"

## 📚 Full Documentation

- **README.md** - Complete system overview and features
- **SETUP_CHECKLIST.md** - Step-by-step setup guide with checkboxes
- **DEPLOYMENT.md** - Production deployment and automation
- **config.template.json** - Example configuration file

## 🎯 What This Does

This system:
1. **Connects** to your Google Sheets campaign data
2. **Processes** and understands your campaigns using AI
3. **Stores** everything in a searchable vector database
4. **Lets you search** using normal questions in English

## 💡 Example Use Cases

### For Daily Work
- "What campaigns are performing best this month?"
- "Show me all wellness brand partnerships"
- "Find campaigns with over 100k impressions"

### For Analysis
- "Compare Q1 vs Q2 performance"
- "What content types get the most engagement?"
- "Which creators perform best with supplement brands?"

### For Reporting
- "Find all campaigns from last quarter for the monthly report"
- "What were our highest revenue campaigns?"
- "Show engagement trends over the year"

## 🔧 Customization

The system is designed to work with your existing data. Simply:

1. Edit the column mappings in `data_ingestion.py` to match your sheet structure
2. Add any custom metrics you track
3. Adjust the query prompts for your specific needs

## 🆘 Troubleshooting

**Something not working?**

```bash
# Run this to diagnose
python test_setup.py
```

**Common fixes:**
- Make sure API keys are set: `echo $PINECONE_API_KEY`
- Check credentials.json exists: `ls credentials.json`
- Verify sheet is shared with service account
- Re-run setup: `python pinecone_setup.py`

## 📞 Support

1. Check **SETUP_CHECKLIST.md** for detailed steps
2. Review **README.md** for feature documentation
3. See **DEPLOYMENT.md** for advanced topics

## 🎉 That's It!

You now have a powerful, AI-driven search system for all your campaign data. No more digging through spreadsheets or trying to remember which quarter a campaign ran!

---

**Ready to start?** Run: `python quick_start.py`

This will guide you through the entire setup process interactively.
