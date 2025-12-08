# ENT Agency Campaign Vector Database

A complete Pinecone-based vector database system for searching and analyzing influencer marketing campaigns using natural language queries.

## 🚀 Features

- **Semantic Search**: Ask questions in natural language about your campaigns
- **Multi-Quarter Analysis**: Compare performance across different time periods
- **Creator Insights**: Analyze individual creator performance
- **Brand Analytics**: Track brand-specific campaign results
- **Metrics Tracking**: Store and query engagement, impressions, revenue, and more
- **Automated Data Ingestion**: Pull data directly from Google Sheets

## 📋 Prerequisites

1. **Pinecone Account**: Sign up at https://www.pinecone.io/
2. **OpenAI API Key**: Get one at https://platform.openai.com/
3. **Google Cloud Project** (for Sheets access):
   - Enable Google Sheets API
   - Create OAuth 2.0 credentials or Service Account

## 🛠️ Installation

### Step 1: Install Dependencies

```bash
pip install pinecone openai gspread oauth2client google-auth google-auth-oauthlib google-api-python-client --break-system-packages
```

### Step 2: Set Up API Keys

Create a `.env` file or export environment variables:

```bash
export PINECONE_API_KEY='your-pinecone-api-key'
export OPENAI_API_KEY='your-openai-api-key'
```

Or create a `.env` file:
```
PINECONE_API_KEY=your-pinecone-api-key
OPENAI_API_KEY=your-openai-api-key
```

### Step 3: Set Up Google Sheets Access

**Option A: Service Account (Recommended for automation)**
1. Go to Google Cloud Console
2. Create a Service Account
3. Download the JSON key file
4. Save it as `credentials.json`
5. Share your Google Sheet with the service account email

**Option B: OAuth (Interactive)**
1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download the JSON file
4. Save it as `credentials.json`

## 📊 Usage

### 1. Initialize Pinecone Index

```bash
python pinecone_setup.py
```

This creates the vector database index in Pinecone.

### 2. Ingest Data from Google Sheets

```bash
python data_ingestion.py
```

This will:
- Connect to your Google Sheets
- Extract campaign data
- Transform it into the proper format
- Load it into Pinecone with embeddings

**To customize for your specific sheet:**

Edit the `main()` function in `data_ingestion.py`:

```python
SPREADSHEET_ID = "your-spreadsheet-id"  # From the URL
sheet_name = "Sheet1"  # Or None for first sheet
quarter = "2024 Q4"  # Optional
creator = "Nicki Entenmann"  # Optional
```

### 3. Query Your Data

**Interactive Mode:**
```bash
python query_interface.py
```

Then choose option 1 for interactive search, or select other options for specific queries.

**Example Queries:**
- "What were our best performing Instagram campaigns in Q1 2024?"
- "Show me all Thorne campaigns with high engagement"
- "Find campaigns by Nicki Entenmann with over 50k impressions"
- "What were our highest revenue campaigns last quarter?"

## 🔧 Customizing Data Structure

The system expects campaign data with these fields (customize in `data_ingestion.py`):

```python
{
    'quarter': '2024 Q4',
    'creator': 'Nicki Entenmann',
    'brand': 'Thorne',
    'campaign_type': 'Instagram Reel',
    'platform': 'Instagram',
    'date': '2024-10-15',
    'metrics': {
        'impressions': 125000,
        'engagement': 8500,
        'clicks': 1200,
        'engagement_rate': 6.8
    },
    'revenue': 2500.00,
    'content_description': 'Product review video',
    'notes': 'High performance on reels'
}
```

### Mapping Your Spreadsheet Columns

Edit the `transform_to_campaign_format()` function in `data_ingestion.py` to match your column names:

```python
campaign['brand'] = row.get('Brand', row.get('Client', ''))
campaign['campaign_type'] = row.get('Type', row.get('Format', ''))
# Add your custom mappings here
```

## 🎯 Use Cases

### 1. Performance Analysis
```python
interface.query_best_performing(metric="engagement", quarter="2024 Q4", top_k=10)
```

### 2. Brand Campaigns
```python
interface.query_by_brand("Thorne", top_k=20)
```

### 3. Creator Performance
```python
interface.query_by_creator("Nicki Entenmann", top_k=15)
```

### 4. Trend Analysis
```python
interface.analyze_trends("wellness campaigns", quarters=["2024 Q1", "2024 Q2", "2024 Q3", "2024 Q4"])
```

### 5. Creator Comparison
```python
interface.compare_creators("Nicki Entenmann", "Sara Preston", metric="engagement")
```

## 📈 Advanced Features

### Metadata Filters

You can filter queries by metadata:

```python
results = db.query(
    query_text="high engagement campaigns",
    top_k=10,
    filter_dict={
        'quarter': '2024 Q4',
        'platform': 'Instagram',
        'creator': 'Nicki Entenmann'
    }
)
```

### Bulk Ingestion

Ingest multiple campaigns at once:

```python
campaigns = [
    {'quarter': '2024 Q4', 'creator': 'Nicki', ...},
    {'quarter': '2024 Q4', 'creator': 'Sara', ...},
    # ... more campaigns
]

db.ingest_bulk_campaigns(campaigns, batch_size=100)
```

## 🔍 Query Examples

1. **Time-based queries:**
   - "Best campaigns in Q1 2024"
   - "Instagram reels from last quarter"
   - "Campaigns posted in October"

2. **Performance queries:**
   - "High engagement rate campaigns"
   - "Campaigns with over 100k impressions"
   - "Top revenue generating posts"

3. **Content queries:**
   - "Product review campaigns"
   - "Story posts about supplements"
   - "Wellness content partnerships"

4. **Comparative queries:**
   - "Compare Instagram vs TikTok performance"
   - "Nicki's best performing brands"
   - "Which creators perform best with Thorne?"

## 🗄️ Database Management

### Check Index Stats
```python
stats = db.get_stats()
print(f"Total vectors: {stats['total_vector_count']}")
```

### Update Campaigns
```python
# Ingest with same ID to update
db.ingest_campaign(updated_campaign_data, campaign_id="existing_id")
```

### Delete Index (if needed)
```python
from pinecone import Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
pc.delete_index("ent-agency-campaigns")
```

## 💡 Tips

1. **Start with one quarter**: Test the system with a single quarter before ingesting all data
2. **Consistent formatting**: Keep date formats and metric names consistent across sheets
3. **Regular updates**: Set up a cron job to automatically ingest new data weekly
4. **Use filters**: Narrow down large result sets with metadata filters
5. **Experiment with queries**: The more specific your query, the better the results

## 🐛 Troubleshooting

**"Index not found" error:**
- Run `python pinecone_setup.py` to create the index first

**Google Sheets authentication fails:**
- Check that your credentials.json is in the correct location
- Verify the Sheet is shared with the service account email
- Make sure Google Sheets API is enabled in Google Cloud

**No results returned:**
- Check that data was successfully ingested
- Try broader queries first
- Verify metadata filters aren't too restrictive

**Rate limit errors:**
- Reduce batch_size in bulk ingestion
- Add delays between API calls

## 📝 File Structure

```
.
├── pinecone_setup.py       # Core vector database setup
├── data_ingestion.py       # Google Sheets extraction & loading
├── query_interface.py      # Search interface
├── credentials.json        # Google credentials (not in repo)
├── .env                    # API keys (not in repo)
└── README.md              # This file
```

## 🔐 Security Notes

- Never commit credentials.json or .env files to version control
- Add them to .gitignore
- Use environment variables in production
- Rotate API keys regularly

## 📞 Support

For questions about:
- **Pinecone**: https://docs.pinecone.io/
- **OpenAI**: https://platform.openai.com/docs
- **Google Sheets API**: https://developers.google.com/sheets/api

## 🎉 Next Steps

1. Run the setup: `python pinecone_setup.py`
2. Ingest your data: `python data_ingestion.py`
3. Start querying: `python query_interface.py`
4. Build custom analytics on top of the query interface
5. Integrate with your existing agency tools

Happy searching! 🚀
