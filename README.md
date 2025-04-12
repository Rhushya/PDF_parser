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
git clone https://github.com/Rhushya/PDF_parser
cd PDF_parser
```

### Step 2: Install dependencies



#### Mac/Linux/Windows
```bash
pip install -r requirements.txt

# Optional dependencies
pip install pdf2image pytesseract

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