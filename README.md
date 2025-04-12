# PDF Parser

A Python-based application for extracting content from PDF files, including text, tables, images, and OCR text.

## Features

- Extract metadata from PDF files
- Extract text content from each page
- Extract tables and convert to CSV
- Extract images from PDF pages
- Perform OCR on images to extract text
- Download all extracted content in a single zip file

## Requirements

### Core Requirements
- Python 3.7+
- Streamlit
- PyMuPDF
- pdfplumber
- Pillow
- pandas

### Optional Requirements
- pdf2image + Poppler (for better image extraction)
- pytesseract + Tesseract OCR (for OCR functionality)

## Installation

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/pdf-parser.git
cd pdf-parser
```

### Step 2: Install dependencies

#### Windows
Run the setup script:
```bash
setup_windows.bat
```

#### Mac/Linux
```bash
pip install -r requirements.txt

# Optional dependencies
pip install pdf2image pytesseract

# On Mac
brew install poppler tesseract

# On Linux
apt-get install poppler-utils tesseract-ocr
```

## Troubleshooting

### Missing Poppler

If you see an error like `Unable to get page count. Is poppler installed and in PATH?`, you need to install Poppler:

#### Windows
1. Download from [GitHub](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Extract to a folder (e.g., `C:\Program Files\poppler`)
3. Add the `bin` folder to your PATH environment variable
4. Restart your terminal and the application

#### Mac
```bash
brew install poppler
```

#### Linux
```bash
apt-get install poppler-utils
```

### Missing Tesseract OCR

If OCR functionality is not working, you need to install Tesseract OCR:

#### Windows
1. Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer
3. Make sure to add Tesseract to your PATH during installation
4. Restart your terminal and the application

#### Mac
```bash
brew install tesseract
```

#### Linux
```bash
apt-get install tesseract-ocr
```

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser. Upload a PDF file and explore the extracted content in the tabs.

## Using Without Optional Dependencies

The application will work even without pdf2image and pytesseract:

- Without pdf2image: The application will fall back to using PyMuPDF for image extraction (lower quality)
- Without pytesseract: OCR functionality will be disabled

## License

MIT
