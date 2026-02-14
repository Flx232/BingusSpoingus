#!/usr/bin/env python3
"""
Test script to verify the setup is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing BingusSpoingus Setup")
print("=" * 50)

# Check Python version
print(f"Python version: {sys.version}")

# Check if required packages are installed
packages_to_check = ['dotenv']
missing_packages = []

for package in packages_to_check:
    try:
        __import__(package)
        print(f"✓ {package} is installed")
    except ImportError:
        print(f"✗ {package} is NOT installed")
        missing_packages.append(package)

# Check Node.js and npx
import subprocess

try:
    result = subprocess.run(['node', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ Node.js is available: {result.stdout.strip()}")
    else:
        print("✗ Node.js is not available")
except FileNotFoundError:
    print("✗ Node.js is not installed")

try:
    result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ npx is available: {result.stdout.strip()}")
    else:
        print("✗ npx is not available")
except FileNotFoundError:
    print("✗ npx is not available")

# Test importing the web search module
try:
    from src.web_search import WebSearchManager, SearchResult
    print("✓ WebSearchManager can be imported")
    print("✓ Web search module is ready to use")
            
except ImportError as e:
    print(f"✗ Cannot import web search module: {e}")

print("\n" + "=" * 50)
if missing_packages:
    print(f"Please install missing packages: pip install -r requirements.txt")
if not os.getenv('ANTHROPIC_API_KEY'):
    print("Please set your Anthropic API key in the .env file")
else:
    print("Setup looks good! You can now run: python examples/topic_parser_example.py")