#!/usr/bin/env python
"""
PDF Parser Launcher Script

This script launches the PDF Parser Streamlit application.
It also checks for the presence of optional dependencies and displays messages accordingly.
"""

import subprocess
import sys
import importlib
import os

def check_dependency(module_name):
    """Check if a Python module is installed."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main():
    """Main function to launch the PDF Parser application."""
    print("Starting PDF Parser application...")
    
    # Check for optional dependencies
    if not check_dependency('pdf2image'):
        print("Note: pdf2image is not installed. Using fallback image extraction method.")
        print("To install: pip install pdf2image")
        print("You'll also need Poppler installed on your system.")
        
    if not check_dependency('pytesseract'):
        print("Note: pytesseract is not installed. OCR functionality will be disabled.")
        print("To install: pip install pytesseract")
        print("You'll also need Tesseract OCR installed on your system.")
    
    # Launch the Streamlit app
    try:
        print("\nLaunching Streamlit application...")
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "app.py"], 
            check=True
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        return 1
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install it with: pip install streamlit")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 