"""
Google Sheets Data Ingestion for ENT Agency Campaigns
This script extracts data from Google Sheets and loads it into Pinecone
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([
        "pip", "install", 
        "gspread", "oauth2client", "google-auth", "google-auth-oauthlib", 
        "google-auth-httplib2", "google-api-python-client",
        "--break-system-packages"
    ])
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

from pinecone_setup import ENTAgencyVectorDB


class GoogleSheetsExtractor:
    """Extract campaign data from Google Sheets"""
    
    def __init__(self, credentials_file: str = None):
        """
        Initialize Google Sheets connection
        
        Args:
            credentials_file: Path to Google service account JSON or OAuth credentials
        """
        self.credentials_file = credentials_file
        self.client = None
        
    def authenticate_service_account(self):
        """Authenticate using service account"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, scope
        )
        self.client = gspread.authorize(creds)
        print("✓ Authenticated with service account")
        
    def authenticate_oauth(self):
        """Authenticate using OAuth (interactive)"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise Exception(f"Credentials file not found: {self.credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.client = gspread.authorize(creds)
        print("✓ Authenticated with OAuth")
    
    def extract_from_sheet(self, spreadsheet_id: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """
        Extract data from a Google Sheet
        
        Args:
            spreadsheet_id: The ID from the Google Sheets URL
            sheet_name: Specific sheet/tab name (uses first sheet if not provided)
        
        Returns:
            List of campaign dictionaries
        """
        if not self.client:
            raise Exception("Not authenticated. Call authenticate_service_account() or authenticate_oauth() first")
        
        print(f"Opening spreadsheet: {spreadsheet_id}")
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        
        if sheet_name:
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
        
        print(f"Reading data from sheet: {worksheet.title}")
        
        # Get all values
        data = worksheet.get_all_records()
        
        print(f"✓ Extracted {len(data)} rows")
        return data
    
    def transform_to_campaign_format(self, raw_data: List[Dict], 
                                     quarter: str = None,
                                     creator: str = None) -> List[Dict[str, Any]]:
        """
        Transform raw spreadsheet data into campaign format
        
        This function should be customized based on your actual spreadsheet structure
        
        Args:
            raw_data: Raw data from Google Sheets
            quarter: Quarter to assign (if not in data)
            creator: Creator name to assign (if not in data)
        
        Returns:
            List of formatted campaign dictionaries
        """
        campaigns = []
        
        for row in raw_data:
            campaign = {}
            
            # Map your actual column names to the expected format
            # Customize these mappings based on your spreadsheet structure
            
            campaign['quarter'] = row.get('Quarter', quarter)
            campaign['creator'] = row.get('Creator', row.get('Influencer', creator))
            campaign['brand'] = row.get('Brand', row.get('Client', ''))
            campaign['campaign_type'] = row.get('Campaign Type', row.get('Type', ''))
            campaign['platform'] = row.get('Platform', '')
            campaign['date'] = row.get('Date', row.get('Post Date', ''))
            campaign['content_description'] = row.get('Description', row.get('Content', ''))
            campaign['notes'] = row.get('Notes', '')
            
            # Extract metrics
            metrics = {}
            metric_fields = [
                'impressions', 'reach', 'engagement', 'likes', 'comments', 
                'shares', 'saves', 'clicks', 'views', 'engagement_rate'
            ]
            
            for field in metric_fields:
                # Try different capitalizations
                for key_variant in [field, field.title(), field.upper(), field.replace('_', ' ').title()]:
                    if key_variant in row:
                        value = row[key_variant]
                        if value and value != '':
                            # Clean and convert to number
                            if isinstance(value, str):
                                value = value.replace(',', '').replace('%', '')
                            try:
                                metrics[field] = float(value)
                            except:
                                pass
                        break
            
            if metrics:
                campaign['metrics'] = metrics
            
            # Extract revenue
            for revenue_key in ['Revenue', 'revenue', 'Earnings', 'earnings', 'Payment', 'payment']:
                if revenue_key in row and row[revenue_key]:
                    try:
                        revenue_value = str(row[revenue_key]).replace('$', '').replace(',', '')
                        campaign['revenue'] = float(revenue_value)
                        break
                    except:
                        pass
            
            campaigns.append(campaign)
        
        return campaigns


def ingest_from_google_sheets(
    spreadsheet_id: str,
    pinecone_api_key: str,
    openai_api_key: str,
    credentials_file: str = None,
    sheet_name: str = None,
    quarter: str = None,
    creator: str = None
):
    """
    Complete pipeline: Extract from Google Sheets and ingest to Pinecone
    
    Args:
        spreadsheet_id: Google Sheets ID from URL
        pinecone_api_key: Pinecone API key
        openai_api_key: OpenAI API key
        credentials_file: Path to Google credentials JSON
        sheet_name: Specific sheet tab name
        quarter: Quarter label (e.g., "2024 Q1")
        creator: Creator name
    """
    print("=" * 60)
    print("Google Sheets → Pinecone Data Ingestion")
    print("=" * 60)
    print()
    
    # Extract from Google Sheets
    extractor = GoogleSheetsExtractor(credentials_file)
    
    try:
        if credentials_file and credentials_file.endswith('.json'):
            extractor.authenticate_service_account()
        else:
            extractor.authenticate_oauth()
    except Exception as e:
        print(f"Authentication failed: {e}")
        print("\nFor OAuth authentication, you need to:")
        print("1. Enable Google Sheets API in Google Cloud Console")
        print("2. Download OAuth 2.0 credentials JSON")
        print("3. Save as 'credentials.json'")
        return
    
    # Extract data
    raw_data = extractor.extract_from_sheet(spreadsheet_id, sheet_name)
    
    if not raw_data:
        print("No data found in spreadsheet")
        return
    
    # Transform data
    print("\nTransforming data...")
    campaigns = extractor.transform_to_campaign_format(raw_data, quarter, creator)
    print(f"✓ Transformed {len(campaigns)} campaigns")
    
    # Initialize Pinecone
    print("\nConnecting to Pinecone...")
    db = ENTAgencyVectorDB(
        pinecone_api_key=pinecone_api_key,
        openai_api_key=openai_api_key
    )
    db.create_index()
    
    # Ingest campaigns
    print("\nIngesting campaigns to Pinecone...")
    db.ingest_bulk_campaigns(campaigns)
    
    print("\n" + "=" * 60)
    print("✓ Data ingestion complete!")
    print("=" * 60)
    print(f"\nTotal campaigns ingested: {len(campaigns)}")
    
    # Show stats
    stats = db.get_stats()
    print(f"Index total vectors: {stats.get('total_vector_count', 0)}")


def main():
    """Example usage"""
    # Your spreadsheet ID from the URL:
    # https://docs.google.com/spreadsheets/d/1MBAXkNJRa1cV_mYfbWltGstaTgCTgHI65q6cbL0POTQ/edit
    SPREADSHEET_ID = "1MBAXkNJRa1cV_mYfbWltGstaTgCTgHI65q6cbL0POTQ"
    
    # Get API keys from environment
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    if not PINECONE_API_KEY or not OPENAI_API_KEY:
        print("ERROR: Please set PINECONE_API_KEY and OPENAI_API_KEY environment variables")
        return
    
    # Run ingestion
    ingest_from_google_sheets(
        spreadsheet_id=SPREADSHEET_ID,
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY,
        credentials_file='credentials.json',  # Your Google credentials
        sheet_name=None,  # Will use first sheet
        quarter="2024 Q4",  # Optional: specify quarter if not in sheet
        creator=None  # Optional: specify creator if not in sheet
    )


if __name__ == "__main__":
    main()
