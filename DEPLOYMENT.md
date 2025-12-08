# Production Deployment Guide

## 🚀 Deploying to Production

### Option 1: Scheduled Updates (Recommended)

Set up a cron job to automatically update your vector database:

```bash
# Edit crontab
crontab -e

# Add one of these lines:

# Update daily at 2 AM
0 2 * * * cd /path/to/project && /usr/bin/python3 auto_update.py >> update.log 2>&1

# Update weekly on Monday at 3 AM
0 3 * * 1 cd /path/to/project && /usr/bin/python3 auto_update.py >> update.log 2>&1

# Update monthly on the 1st at midnight
0 0 1 * * cd /path/to/project && /usr/bin/python3 auto_update.py >> update.log 2>&1
```

### Option 2: AWS Lambda (Serverless)

Deploy as a serverless function that runs on schedule:

1. **Package the code:**
```bash
pip install -r requirements.txt -t ./package
cp *.py ./package/
cd package
zip -r ../deployment.zip .
```

2. **Create Lambda function:**
- Runtime: Python 3.11
- Memory: 512 MB (adjust based on data size)
- Timeout: 5 minutes
- Upload deployment.zip

3. **Set environment variables:**
- `PINECONE_API_KEY`
- `OPENAI_API_KEY`

4. **Add EventBridge trigger:**
- Schedule expression: `cron(0 2 * * ? *)` for daily at 2 AM UTC

### Option 3: Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY credentials.json .

ENV PYTHONUNBUFFERED=1

CMD ["python", "auto_update.py"]
```

Build and run:
```bash
docker build -t ent-agency-vectordb .
docker run -e PINECONE_API_KEY=$PINECONE_API_KEY \
           -e OPENAI_API_KEY=$OPENAI_API_KEY \
           ent-agency-vectordb
```

### Option 4: GitHub Actions

Create `.github/workflows/update-database.yml`:

```yaml
name: Update Vector Database

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run update
      env:
        PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        echo "${{ secrets.GOOGLE_CREDENTIALS }}" > credentials.json
        python auto_update.py
```

## 🔐 Security Best Practices

### 1. API Key Management

**Never commit API keys to version control!**

Use one of these methods:

**Environment Variables (Linux/Mac):**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PINECONE_API_KEY='your-key'
export OPENAI_API_KEY='your-key'
```

**AWS Secrets Manager:**
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('ent-agency-vectordb')
PINECONE_API_KEY = secrets['PINECONE_API_KEY']
OPENAI_API_KEY = secrets['OPENAI_API_KEY']
```

**Google Secret Manager:**
```python
from google.cloud import secretmanager

def get_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')
```

### 2. Credentials Encryption

Encrypt your credentials.json:

```bash
# Encrypt
openssl enc -aes-256-cbc -salt -in credentials.json -out credentials.json.enc

# Decrypt (in production)
openssl enc -aes-256-cbc -d -in credentials.json.enc -out credentials.json
```

### 3. Access Control

**Pinecone:**
- Create separate indexes for dev/staging/prod
- Use API key rotation
- Enable IP allowlisting if available

**Google Sheets:**
- Use service accounts with minimal permissions
- Only share sheets that need to be accessed
- Regularly audit access logs

## 📊 Monitoring & Logging

### Setup Logging

Add to your scripts:

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/update_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use in code
logger.info("Starting data ingestion")
logger.error(f"Failed to process campaign: {e}")
```

### Monitor Pinecone Usage

```python
def check_pinecone_usage(api_key):
    """Monitor index size and query usage"""
    pc = Pinecone(api_key=api_key)
    index = pc.Index("ent-agency-campaigns")
    
    stats = index.describe_index_stats()
    
    print(f"Total vectors: {stats['total_vector_count']}")
    print(f"Dimensions: {stats['dimension']}")
    
    # Alert if getting close to limits
    if stats['total_vector_count'] > 90000:  # Example threshold
        logger.warning("Approaching vector limit!")
```

### Set Up Alerts

**Email Alerts (using SendGrid):**

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_alert(subject, message):
    message = Mail(
        from_email='alerts@yourdomain.com',
        to_emails='you@yourdomain.com',
        subject=subject,
        html_content=message
    )
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Alert sent: {response.status_code}")
    except Exception as e:
        print(f"Error sending alert: {e}")
```

**Slack Alerts:**

```python
import requests

def send_slack_alert(webhook_url, message):
    """Send alert to Slack channel"""
    payload = {
        'text': message,
        'username': 'Vector DB Bot',
        'icon_emoji': ':robot_face:'
    }
    
    requests.post(webhook_url, json=payload)
```

## 🔄 Backup & Recovery

### Backup Strategy

```python
def backup_pinecone_index(api_key, index_name):
    """Export all vectors from Pinecone"""
    import json
    from datetime import datetime
    
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    # Get all vector IDs (implement pagination if needed)
    stats = index.describe_index_stats()
    
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'index_name': index_name,
        'stats': stats,
        'vectors': []
    }
    
    # Note: Pinecone doesn't have a direct export API
    # You'll need to maintain your own backup of source data
    
    backup_file = f"backups/pinecone_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"Backup saved to {backup_file}")
```

### Restore Process

```python
def restore_from_backup(backup_file, api_key):
    """Restore vectors from backup"""
    import json
    
    with open(backup_file, 'r') as f:
        backup_data = json.load(f)
    
    # Re-ingest all campaigns
    db = ENTAgencyVectorDB(api_key, openai_api_key)
    db.create_index()
    
    # Restore vectors (you'll need your source data)
    # This is why maintaining your Google Sheets is crucial
```

## 📈 Performance Optimization

### 1. Batch Processing

Process campaigns in batches to reduce API calls:

```python
# Good - Batch processing
db.ingest_bulk_campaigns(campaigns, batch_size=100)

# Avoid - Individual processing
for campaign in campaigns:
    db.ingest_campaign(campaign)  # Too many API calls
```

### 2. Caching

Implement query caching for common searches:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query_text, top_k):
    return db.query(query_text, top_k)
```

### 3. Index Optimization

Use appropriate index settings:

```python
# For better accuracy
spec = ServerlessSpec(cloud="aws", region="us-east-1")

# Consider metadata filtering to reduce search space
results = db.query(
    query_text="high engagement",
    filter_dict={'quarter': '2024 Q4'},  # Narrows search
    top_k=10
)
```

## 🧪 Testing

### Unit Tests

Create `test_vectordb.py`:

```python
import unittest
from pinecone_setup import ENTAgencyVectorDB

class TestVectorDB(unittest.TestCase):
    
    def setUp(self):
        self.db = ENTAgencyVectorDB(
            pinecone_api_key=os.getenv('PINECONE_API_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            index_name="test-index"
        )
    
    def test_embedding_generation(self):
        text = "Test campaign"
        embedding = self.db.get_embedding(text)
        self.assertEqual(len(embedding), 1536)
    
    def test_campaign_ingestion(self):
        campaign = {
            'quarter': '2024 Q4',
            'creator': 'Test Creator',
            'brand': 'Test Brand'
        }
        campaign_id = self.db.ingest_campaign(campaign)
        self.assertIsNotNone(campaign_id)

if __name__ == '__main__':
    unittest.main()
```

## 📱 Integration Ideas

### 1. Slack Bot

Create a Slack bot for querying campaigns:

```python
from slack_bolt import App

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/campaigns")
def handle_campaign_query(ack, command):
    ack()
    
    query = command['text']
    results = db.query(query, top_k=5)
    
    # Format and send results
    ...
```

### 2. Web Dashboard

Create a simple Flask API:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/search', methods=['POST'])
def search_campaigns():
    query = request.json.get('query')
    results = db.query(query, top_k=10)
    return jsonify(results)
```

### 3. Zapier Integration

Create a webhook endpoint for Zapier automation.

## 🎯 Next Steps

1. Choose your deployment method
2. Set up monitoring and alerts
3. Implement backup strategy
4. Test in staging environment
5. Deploy to production
6. Monitor and optimize

Good luck! 🚀
