#!/usr/bin/env python3
"""
Quick Start Script for ENT Agency Vector Database
This script guides you through the complete setup process
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_step(number, text):
    """Print a step number"""
    print(f"\n{'='*70}")
    print(f"STEP {number}: {text}")
    print('='*70 + "\n")


def check_env_var(var_name):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if value:
        print(f"✓ {var_name} is set")
        return True
    else:
        print(f"✗ {var_name} is not set")
        return False


def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    packages = [
        "pinecone",
        "openai",
        "gspread",
        "oauth2client",
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client"
    ]
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            *packages, "--break-system-packages", "--quiet"
        ])
        print("✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False


def setup_env_file():
    """Create or update .env file"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("Found existing .env file")
        update = input("Do you want to update it? (y/n): ").strip().lower()
        if update != 'y':
            return True
    
    print("\nLet's set up your API keys...")
    print("(Press Enter to skip if already set in environment)")
    
    pinecone_key = input("\nPinecone API Key: ").strip()
    openai_key = input("OpenAI API Key: ").strip()
    
    if not pinecone_key:
        pinecone_key = os.getenv('PINECONE_API_KEY', '')
    if not openai_key:
        openai_key = os.getenv('OPENAI_API_KEY', '')
    
    if pinecone_key and openai_key:
        with open(".env", "w") as f:
            f.write(f"PINECONE_API_KEY={pinecone_key}\n")
            f.write(f"OPENAI_API_KEY={openai_key}\n")
        print("✓ .env file created")
        return True
    else:
        print("✗ API keys are required")
        return False


def setup_google_credentials():
    """Check for Google credentials"""
    creds_file = Path("credentials.json")
    
    if creds_file.exists():
        print("✓ Found credentials.json")
        return True
    
    print("✗ Google credentials not found")
    print("\nYou need to set up Google Sheets access:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a project and enable Google Sheets API")
    print("3. Create credentials (Service Account or OAuth 2.0)")
    print("4. Download the JSON file and save as 'credentials.json'")
    print("5. Share your Google Sheet with the service account email")
    
    return False


def create_pinecone_index():
    """Create Pinecone index"""
    print("Creating Pinecone index...")
    try:
        subprocess.check_call([sys.executable, "pinecone_setup.py"])
        print("✓ Pinecone index created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating index: {e}")
        return False


def configure_data_source():
    """Configure Google Sheets data source"""
    print("\nLet's configure your data source...")
    
    spreadsheet_id = input("\nGoogle Sheets ID (from URL): ").strip()
    if not spreadsheet_id:
        print("Using default from example")
        spreadsheet_id = "1MBAXkNJRa1cV_mYfbWltGstaTgCTgHI65q6cbL0POTQ"
    
    sheet_name = input("Sheet name (press Enter for first sheet): ").strip() or None
    quarter = input("Default quarter (e.g., '2024 Q4', optional): ").strip() or None
    creator = input("Default creator (optional): ").strip() or None
    
    # Create config file
    config = {
        'spreadsheet_id': spreadsheet_id,
        'sheet_name': sheet_name,
        'quarter': quarter,
        'creator': creator
    }
    
    import json
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration saved to config.json")
    return True


def main():
    """Main setup wizard"""
    print_header("ENT Agency Vector Database - Quick Start Setup")
    
    print("This wizard will guide you through setting up your vector database.")
    print("You'll need:")
    print("  • Pinecone API key")
    print("  • OpenAI API key")
    print("  • Google Sheets credentials")
    print("  • Your Google Sheets ID")
    
    proceed = input("\nReady to start? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Setup cancelled.")
        return
    
    # Step 1: Install dependencies
    print_step(1, "Installing Dependencies")
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        return
    
    # Step 2: Set up API keys
    print_step(2, "Setting Up API Keys")
    
    # Check existing env vars
    pinecone_set = check_env_var('PINECONE_API_KEY')
    openai_set = check_env_var('OPENAI_API_KEY')
    
    if not (pinecone_set and openai_set):
        if not setup_env_file():
            print("\n❌ Setup failed at API key configuration")
            print("\nYou can manually create a .env file with:")
            print("  PINECONE_API_KEY=your-key")
            print("  OPENAI_API_KEY=your-key")
            return
    
    # Step 3: Google credentials
    print_step(3, "Checking Google Sheets Access")
    has_google_creds = setup_google_credentials()
    
    # Step 4: Create Pinecone index
    print_step(4, "Creating Pinecone Index")
    if not create_pinecone_index():
        print("\n❌ Setup failed at Pinecone index creation")
        return
    
    # Step 5: Configure data source
    print_step(5, "Configuring Data Source")
    if not configure_data_source():
        print("\n❌ Setup failed at data source configuration")
        return
    
    # Final summary
    print_header("Setup Complete! 🎉")
    
    print("✓ Dependencies installed")
    print("✓ API keys configured")
    print("✓ Pinecone index created")
    print("✓ Data source configured")
    
    if has_google_creds:
        print("✓ Google credentials ready")
    else:
        print("⚠ Google credentials need to be set up manually")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    
    if not has_google_creds:
        print("\n1. Set up Google Sheets credentials:")
        print("   - Follow the instructions above to get credentials.json")
    
    print("\n2. Ingest your data:")
    print("   python data_ingestion.py")
    
    print("\n3. Start querying:")
    print("   python query_interface.py")
    
    print("\n" + "="*70)
    print("For detailed documentation, see README.md")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("Please check the logs and try again.")
