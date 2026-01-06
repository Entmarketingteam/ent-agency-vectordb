# Offline/Network Issue Package Installation

If you're experiencing network issues installing packages, here are alternative methods:

## Method 1: Download Wheel Files Manually

1. **Download packages from PyPI:**
   - Go to: https://pypi.org/project/pinecone/#files
   - Download the `.whl` file for your Python version (Python 3.12)
   - Do the same for `openai` and `python-dotenv`

2. **Install from local files:**
   ```powershell
   pip install path/to/pinecone-*.whl --break-system-packages
   pip install path/to/openai-*.whl --break-system-packages
   pip install path/to/python_dotenv-*.whl --break-system-packages
   ```

## Method 2: Use Different Network

- Try mobile hotspot
- Use different WiFi network
- Use VPN if available
- Try from home network instead of corporate

## Method 3: Configure Proxy

If behind corporate firewall:

```powershell
# Set proxy environment variable
$env:HTTP_PROXY="http://proxy.company.com:8080"
$env:HTTPS_PROXY="http://proxy.company.com:8080"

# Then install
pip install pinecone openai python-dotenv --break-system-packages
```

## Method 4: Use Conda/Miniconda

If pip isn't working, try conda:

```powershell
conda install -c conda-forge openai
pip install pinecone --break-system-packages  # Pinecone may not be in conda
```

## Method 5: Contact IT

If you're on a corporate network:
- Contact IT to whitelist pypi.org
- Ask for pip proxy configuration
- Request package installation assistance

## Verify Installation

After installing, verify:

```powershell
python check_packages.py
```

This will show what's installed and what's missing.


