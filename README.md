# PDF Parser

A streamlined Python application for extracting content from PDF files, including text, tables, images, and OCR text.

## Features

- Extract metadata from PDF files
- Extract text content from each page
- Extract tables and convert to CSV
- Extract images from PDF pages
- Perform OCR on images to extract text (optional)
- Download all extracted content in a single zip file

## Setup with Conda

This guide provides step-by-step instructions to set up the PDF Parser using Conda, which handles dependencies in a clean environment.

### Step 1: Install Miniconda (if not already installed)

If you don't have Conda installed, download and install Miniconda:

#### Windows:
1. Download [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Windows
2. Run the installer and follow the instructions

#### Mac:
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh
```

#### Linux:
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### Step 2: Clone the Repository

```bash
# Clone the repository (if using git)
git clone https://github.com/yourusername/pdf-parser.git
cd pdf-parser

# Alternatively, download and extract the ZIP file
```

### Step 3: Create and Setup Conda Environment

#### Option 1: Using environment.yml (Recommended)

```bash
# Create the environment from the environment.yml file
conda env create -f environment.yml

# Activate the environment
conda activate pdfparser
```

#### Option 2: Manual Setup

```bash
# Create a new conda environment called 'pdfparser'
conda create -n pdfparser python=3.10 -y

# Activate the environment
conda activate pdfparser

# Install core dependencies using pip
pip install -r requirements.txt
```

### Step 4: Install Optional Dependencies (For Enhanced Features)

For better image extraction and OCR:

#### Windows:
```bash
# Install Python packages
pip install pdf2image pytesseract

# Install Poppler (for pdf2image)
# 1. Download from https://github.com/oschwartz10612/poppler-windows/releases/
# 2. Extract to a folder (e.g., C:\Program Files\poppler)
# 3. Add the bin folder to your PATH environment variable:
#    - Right-click on 'This PC' > Properties > Advanced system settings > Environment Variables
#    - Edit 'Path' variable and add the path to the bin folder (e.g., C:\Program Files\poppler\bin)

# Install Tesseract OCR (for pytesseract)
# 1. Download from https://github.com/UB-Mannheim/tesseract/wiki
# 2. Run the installer
# 3. Make sure to select "Add to PATH" during installation
```

#### Mac:
```bash
# Install Python packages
pip install pdf2image pytesseract

# Install system dependencies
brew install poppler tesseract
```

#### Linux:
```bash
# Install Python packages
pip install pdf2image pytesseract

# Install system dependencies
sudo apt-get install poppler-utils tesseract-ocr
```

### Step 5: Run the Application

You have two options to run the application:

#### Option 1: Using the run script (Recommended)

```bash
# With the conda environment activated
python run.py
```

This script will check for optional dependencies and provide helpful messages before launching the application.

#### Option 2: Using Streamlit directly

```bash
# With the conda environment activated
streamlit run app.py
```

The application will open in your default web browser, typically at http://localhost:8501

## Usage

1. Upload a PDF file using the file uploader
2. Wait for the processing to complete (this may take a moment depending on the PDF size)
3. Explore the extracted content across the different tabs:
   - **Metadata**: View document properties
   - **Text**: View extracted text by page
   - **Tables**: View and download extracted tables
   - **Images & OCR**: View page images and OCR text (if available)
4. Use the "Download All Results" button to get a ZIP file with all extracted content

## Core vs. Enhanced Functionality

The application works with just the core dependencies but has enhanced functionality with optional components:

- **Core functionality**: Text extraction, table extraction, basic image extraction
- **Enhanced functionality** (with optional dependencies):
  - Better quality image extraction (with pdf2image + Poppler)
  - OCR text extraction from images (with pytesseract + Tesseract)

## Project Structure

```
pdf-parser/
├── app.py                # Main Streamlit application
├── run.py                # Launcher script with dependency checks
├── utils/
│   └── pdf_parser.py     # PDF parsing functionality
├── requirements.txt      # Python dependencies
├── environment.yml       # Conda environment specification
├── uv.lock               # Locked dependencies for reproducibility
└── README.md             # This file
```

## License

MIT
