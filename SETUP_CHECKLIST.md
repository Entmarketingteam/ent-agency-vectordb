# 🎯 ENT Agency Vector Database - Setup Checklist

Use this checklist to ensure your system is fully set up and ready to use.

## ✅ Pre-Setup Checklist

### 1. Get Your API Keys

- [ ] **Pinecone API Key**
  - Sign up at https://www.pinecone.io/
  - Create a new project
  - Copy your API key
  - Keep it secure!

- [ ] **OpenAI API Key**
  - Sign up at https://platform.openai.com/
  - Add payment method (required for API access)
  - Create a new API key
  - Keep it secure!

- [ ] **Google Cloud Setup** (for Sheets access)
  - Create project at https://console.cloud.google.com/
  - Enable Google Sheets API
  - Create Service Account OR OAuth 2.0 credentials
  - Download credentials JSON file

### 2. Prepare Your Data

- [ ] Locate your Google Sheets with campaign data
- [ ] Note the Spreadsheet ID from the URL:
  ```
  https://docs.google.com/spreadsheets/d/[THIS_IS_YOUR_ID]/edit
  ```
- [ ] If using Service Account, share the sheet with the service account email
- [ ] Verify you have the necessary columns in your sheet

## 🚀 Installation Checklist

### Step 1: Download the System

- [ ] Download all files to a folder on your computer
- [ ] Navigate to the folder in terminal/command prompt

### Step 2: Install Dependencies

- [ ] Run: `pip install -r requirements.txt --break-system-packages`
- [ ] Verify installation: `python test_setup.py`

### Step 3: Configure API Keys

Choose ONE method:

**Method A: Environment Variables**
- [ ] On Mac/Linux:
  ```bash
  export PINECONE_API_KEY='your-key-here'
  export OPENAI_API_KEY='your-key-here'
  ```
- [ ] On Windows:
  ```cmd
  set PINECONE_API_KEY=your-key-here
  set OPENAI_API_KEY=your-key-here
  ```

**Method B: .env File**
- [ ] Create a file named `.env`
- [ ] Add these lines:
  ```
  PINECONE_API_KEY=your-key-here
  OPENAI_API_KEY=your-key-here
  ```

### Step 4: Add Google Credentials

- [ ] Save your Google credentials JSON as `credentials.json`
- [ ] Place it in the same folder as the scripts
- [ ] Verify: `ls credentials.json` (should show the file)

### Step 5: Configure Your Data Source

- [ ] Copy `config.template.json` to `config.json`
- [ ] Edit `config.json` with your details:
  ```json
  {
    "spreadsheet_id": "YOUR_SPREADSHEET_ID",
    "sheet_name": "Sheet1",
    "quarter": "2024 Q4",
    "creator": "Your Creator Name"
  }
  ```

## 🧪 Testing Checklist

- [ ] Run test script: `python test_setup.py`
- [ ] Verify all tests pass:
  - [ ] Imports ✓
  - [ ] Environment variables ✓
  - [ ] Google credentials ✓
  - [ ] Pinecone connection ✓
  - [ ] OpenAI connection ✓

## 🗄️ Database Setup Checklist

### Create Pinecone Index

- [ ] Run: `python pinecone_setup.py`
- [ ] Verify you see: "✓ Pinecone index created successfully!"
- [ ] Check Pinecone dashboard to confirm index exists

### Ingest Your Data

- [ ] Update `data_ingestion.py` with your spreadsheet ID (line ~210)
- [ ] Run: `python data_ingestion.py`
- [ ] Wait for completion (may take a few minutes)
- [ ] Verify: "✓ Data ingestion complete!"

## 🔍 Query System Checklist

### Test Your Queries

- [ ] Run: `python query_interface.py`
- [ ] Choose option 1 for interactive mode
- [ ] Try a test query: "What are our best campaigns?"
- [ ] Verify you get results
- [ ] Try specific queries:
  - [ ] "Show campaigns from Q1 2024"
  - [ ] "Find high engagement Instagram posts"
  - [ ] "What were our Thorne campaigns?"

## 📊 Verification Checklist

Confirm everything works:

- [ ] **Data Ingestion**: Can successfully load campaigns from Google Sheets
- [ ] **Search Works**: Natural language queries return relevant results
- [ ] **Filters Work**: Can filter by quarter, creator, brand, etc.
- [ ] **Performance**: Queries return results within 2-3 seconds
- [ ] **Accuracy**: Top results are actually relevant to queries

## 🔄 Automation Setup (Optional)

For automated updates:

- [ ] Decide update frequency (daily/weekly/monthly)
- [ ] Set up cron job (Linux/Mac) or Task Scheduler (Windows)
- [ ] Test automated update: `python auto_update.py`
- [ ] Verify logs are being created

## 🛡️ Security Checklist

- [ ] Never commit `.env` file to Git
- [ ] Never commit `credentials.json` to Git
- [ ] Keep API keys secure and private
- [ ] Use `.gitignore` to prevent accidental commits
- [ ] Rotate API keys every 90 days
- [ ] Limit Google Sheet sharing to necessary accounts

## 📈 Production Checklist (If Deploying)

- [ ] Choose deployment method (see DEPLOYMENT.md)
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy
- [ ] Test in staging environment first
- [ ] Document any custom modifications
- [ ] Train team members on usage

## 🎓 Learning Checklist

Understand the system:

- [ ] Read through README.md
- [ ] Understand basic query syntax
- [ ] Know how to add new data sources
- [ ] Understand metadata filtering
- [ ] Know how to interpret relevance scores

## 📝 Common Issues Checklist

If things aren't working:

- [ ] Check API keys are set correctly
- [ ] Verify Google credentials file exists
- [ ] Confirm spreadsheet is shared with service account
- [ ] Check internet connection
- [ ] Review error messages in terminal
- [ ] Check Pinecone and OpenAI dashboard for API issues
- [ ] Verify spreadsheet ID is correct
- [ ] Make sure index was created successfully

## 🎉 You're Done!

Once all items are checked:

✅ Your vector database is fully operational
✅ You can search campaigns with natural language
✅ Your data is being updated regularly
✅ The system is secure and backed up

## 🆘 Quick Reference

**Check if everything is working:**
```bash
python test_setup.py
```

**Update data from Google Sheets:**
```bash
python data_ingestion.py
```

**Search your campaigns:**
```bash
python query_interface.py
```

**Automated update:**
```bash
python auto_update.py
```

## 📞 Need Help?

Common solutions:
1. Run `python test_setup.py` to diagnose issues
2. Check README.md for detailed instructions
3. Review DEPLOYMENT.md for advanced setups
4. Verify all API keys are correct
5. Make sure all files are in the same directory

## 🔄 Maintenance Schedule

Set reminders:

- [ ] **Daily/Weekly**: Run auto_update.py (if not automated)
- [ ] **Monthly**: Review query performance and usage
- [ ] **Quarterly**: Audit access and rotate API keys
- [ ] **Annually**: Review and optimize index structure

---

**Current Status:** [ ] Setup Complete ✅

**Date Completed:** _______________

**Notes:** 
_____________________________________________
_____________________________________________
_____________________________________________
