#!/usr/bin/env python3
"""Check if required packages are installed"""

import sys

packages = {
    'pinecone': 'Pinecone SDK',
    'openai': 'OpenAI SDK',
    'dotenv': 'python-dotenv'
}

print("Checking installed packages...")
print("=" * 50)

all_installed = True
for package, name in packages.items():
    try:
        __import__(package)
        print(f"OK {name} is installed")
    except ImportError:
        print(f"FAIL {name} is NOT installed")
        all_installed = False

print("=" * 50)

if all_installed:
    print("\nSUCCESS: All packages are installed!")
    print("You can now run: python setup_pinecone.py")
else:
    print("\nERROR: Some packages are missing.")
    print("\nInstallation options:")
    print("1. Try: pip install pinecone openai python-dotenv --break-system-packages")
    print("2. If network issues, see INSTALL_PACKAGES.md")
    print("3. Install manually from downloaded wheel files")

sys.exit(0 if all_installed else 1)


