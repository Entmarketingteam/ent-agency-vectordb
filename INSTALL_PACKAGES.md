# 📦 Installing Packages

You need to install the required packages to use the Pinecone vector database.

## Quick Install

```powershell
pip install -r requirements.txt --break-system-packages
```

## Individual Packages

If the above doesn't work, try installing individually:

```powershell
pip install pinecone --break-system-packages
pip install openai --break-system-packages
pip install python-dotenv --break-system-packages
```

## Network/Proxy Issues

If you're behind a corporate firewall or have network issues:

### Option 1: Configure pip proxy
```powershell
pip install --proxy http://proxy.company.com:8080 pinecone --break-system-packages
```

### Option 2: Use different network
- Try a different WiFi network
- Use mobile hotspot
- Use VPN if available

### Option 3: Manual installation
1. Download packages from PyPI manually
2. Install from local files

## Verify Installation

After installing, verify it works:

```powershell
python -c "import pinecone; print('Pinecone installed!')"
python -c "import openai; print('OpenAI installed!')"
```

## Current Status

Run this to check what's installed:

```powershell
python setup_pinecone.py
```

This will show you:
- ✅ What's installed
- ❌ What's missing
- 🔧 Next steps

## Once Packages Are Installed

After successful installation:

1. **Create/verify Pinecone index:**
   ```powershell
   python setup_pinecone.py
   ```

2. **Or use the main setup:**
   ```powershell
   python pinecone_setup.py
   ```

3. **Then ingest data:**
   ```powershell
   python data_ingestion.py
   ```

4. **Query your data:**
   ```powershell
   python query_interface.py
   ```


