"""
Automated Data Update Script for ENT Agency Vector Database
Run this script periodically to keep your vector database up-to-date
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from data_ingestion import ingest_from_google_sheets


def load_config():
    """Load configuration from config.json"""
    config_file = Path("config.json")
    
    if not config_file.exists():
        print("❌ config.json not found. Run quick_start.py first.")
        return None
    
    with open(config_file, 'r') as f:
        return json.load(f)


def get_current_quarter():
    """Determine current quarter"""
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year} Q{quarter}"


def update_database(spreadsheet_id, sheet_name=None, quarter=None, creator=None):
    """Update the vector database with latest data"""
    
    print("\n" + "="*70)
    print("  ENT Agency Vector Database - Automated Update")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Spreadsheet: {spreadsheet_id}")
    if sheet_name:
        print(f"Sheet: {sheet_name}")
    if quarter:
        print(f"Quarter: {quarter}")
    if creator:
        print(f"Creator: {creator}")
    
    # Get API keys
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    if not PINECONE_API_KEY or not OPENAI_API_KEY:
        print("\n❌ API keys not found in environment")
        print("Set PINECONE_API_KEY and OPENAI_API_KEY")
        return False
    
    try:
        # Run ingestion
        ingest_from_google_sheets(
            spreadsheet_id=spreadsheet_id,
            pinecone_api_key=PINECONE_API_KEY,
            openai_api_key=OPENAI_API_KEY,
            credentials_file='credentials.json',
            sheet_name=sheet_name,
            quarter=quarter,
            creator=creator
        )
        
        print("\n✅ Database update completed successfully!")
        
        # Log the update
        log_update(spreadsheet_id, sheet_name, quarter)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Update failed: {e}")
        return False


def log_update(spreadsheet_id, sheet_name, quarter):
    """Log update to file"""
    log_file = Path("update_log.txt")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} | {spreadsheet_id} | {sheet_name or 'default'} | {quarter or 'auto'}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)


def update_multiple_sheets(sheet_configs):
    """
    Update from multiple sheets/quarters
    
    Args:
        sheet_configs: List of dicts with 'spreadsheet_id', 'sheet_name', 'quarter', 'creator'
    """
    print(f"\n📊 Updating {len(sheet_configs)} data sources...")
    
    success_count = 0
    for i, config in enumerate(sheet_configs, 1):
        print(f"\n[{i}/{len(sheet_configs)}] Processing: {config.get('sheet_name', 'default')}")
        
        if update_database(
            spreadsheet_id=config['spreadsheet_id'],
            sheet_name=config.get('sheet_name'),
            quarter=config.get('quarter'),
            creator=config.get('creator')
        ):
            success_count += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Successfully updated {success_count}/{len(sheet_configs)} data sources")
    print('='*70 + "\n")


def main():
    """Main function"""
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Usage:")
            print("  python auto_update.py              # Use config.json")
            print("  python auto_update.py <sheet_id>   # Update specific sheet")
            print("  python auto_update.py --current    # Update current quarter")
            return
        
        elif sys.argv[1] == '--current':
            # Update current quarter only
            config = load_config()
            if not config:
                return
            
            current_q = get_current_quarter()
            print(f"Updating current quarter: {current_q}")
            
            update_database(
                spreadsheet_id=config['spreadsheet_id'],
                sheet_name=config.get('sheet_name'),
                quarter=current_q,
                creator=config.get('creator')
            )
            return
        
        else:
            # Use provided spreadsheet ID
            spreadsheet_id = sys.argv[1]
            sheet_name = sys.argv[2] if len(sys.argv) > 2 else None
            quarter = sys.argv[3] if len(sys.argv) > 3 else None
            
            update_database(spreadsheet_id, sheet_name, quarter)
            return
    
    # Use config.json
    config = load_config()
    if not config:
        return
    
    # Check if it's a multi-sheet config
    if isinstance(config, list):
        update_multiple_sheets(config)
    else:
        update_database(
            spreadsheet_id=config['spreadsheet_id'],
            sheet_name=config.get('sheet_name'),
            quarter=config.get('quarter'),
            creator=config.get('creator')
        )


if __name__ == "__main__":
    main()
