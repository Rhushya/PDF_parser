# 📄 PDF Parser - Advanced PDF Content Extraction Tool

A sophisticated Python-based application for comprehensive PDF content extraction, including text, tables, images, and OCR processing. Built with Streamlit for an intuitive web interface.

## 🎯 Overview

PDF Parser is a robust document processing tool that leverages multiple state-of-the-art libraries to extract every possible element from PDF documents. It automatically adapts to available dependencies, providing fallback options to ensure functionality even with minimal installations.

## ✨ Key Features

### Core Functionality
- **📊 Metadata Extraction**: Comprehensive document properties including title, author, creation date, page count
- **📝 Text Extraction**: Multiple extraction methods with markdown formatting support
- **📋 Table Extraction**: Automatic detection and conversion of tables to pandas DataFrames and CSV
- **🖼️ Image Extraction**: Full-page image rendering with configurable DPI
- **🔍 OCR Processing**: Optical Character Recognition with multiple engine support
- **📦 Batch Download**: Export all extracted content as a single ZIP archive
- **🎨 Interactive UI**: Streamlit-powered interface with tabbed navigation and live preview

### Advanced Capabilities
- **Adaptive Dependency Management**: Automatic fallback to alternative methods when optional libraries are unavailable
- **Enhanced Text Extraction**: PyMuPDF4LLM integration for superior layout preservation and markdown formatting
- **Dual OCR Support**: Works with both pytesseract and PyMuPDF's built-in OCR engine
- **High-Quality Image Rendering**: 300 DPI image extraction for maximum clarity
- **Error Resilient**: Graceful handling of corrupted pages or extraction failures
- **Memory Efficient**: Temporary file handling with automatic cleanup

## 🏗️ Architecture & Technical Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Web UI                        │
│  (File Upload → Processing → Tabbed Results → Downloads)    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PDFParser Core Engine                     │
│  ┌──────────────┬──────────────┬────────────┬─────────────┐ │
│  │   Metadata   │     Text     │   Tables   │   Images    │ │
│  │  Extraction  │  Extraction  │ Extraction │ Extraction  │ │
│  └──────────────┴──────────────┴────────────┴─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
      ┌──────────────────┼──────────────────┐
      ▼                  ▼                  ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│ PyMuPDF  │      │pdfplumber│      │pdf2image │
│  (fitz)  │      │(Tables)  │      │(Images)  │
└──────────┘      └──────────┘      └──────────┘
      │                                   │
      ▼                                   ▼
┌──────────┐                        ┌──────────┐
│pymupdf4llm│                       │pytesseract│
│(Enhanced │                        │   (OCR)  │
│  Text)   │                        └──────────┘
└──────────┘
```

### Component Breakdown

#### 1. **Streamlit Frontend (app.py)**
- **Purpose**: User interface and orchestration
- **Responsibilities**:
  - File upload handling
  - Temporary directory management
  - Result visualization in tabs
  - Download functionality
  - Dependency status notifications

#### 2. **PDFParser Core (utils/pdf_parser.py)**
- **Purpose**: Core extraction engine
- **Key Methods**:
  - `process_pdf()`: Main orchestrator for all extraction tasks
  - `_extract_text_pymupdf4llm()`: Enhanced text extraction with layout preservation
  - `_extract_images_pymupdf()`: Fallback image extraction
  - `_perform_pymupdf_ocr()`: PyMuPDF-based OCR
  - `save_results()`: Export extracted content to filesystem

#### 3. **Dependency Chain**
```
Core (Required):
├── PyMuPDF (fitz) → Metadata, Text, Base Images
├── pdfplumber → Table Detection & Extraction
├── Pillow (PIL) → Image Manipulation
├── pandas → Table DataFrame Conversion
└── Streamlit → Web Interface

Optional (Enhanced Features):
├── pymupdf4llm → Advanced Text Extraction
├── pdf2image → High-Quality Image Rendering
│   └── Poppler (System) → PDF to Image Conversion
└── pytesseract → OCR Engine
    └── Tesseract (System) → OCR Engine Binary
```

## 🔬 How It Works: Detailed Technical Flow

### 1. PDF Upload & Initialization
```python
# User uploads PDF → Streamlit receives file
uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])

# Temporary directory created for isolated processing
with tempfile.TemporaryDirectory() as temp_dir:
    pdf_path = os.path.join(temp_dir, uploaded_file.name)
    # Write uploaded bytes to temporary file
```

### 2. Metadata Extraction Process
```
PyMuPDF opens PDF → Read document.metadata dictionary
↓
Extract standard PDF properties:
├── Title, Author, Subject
├── Creator, Producer
├── Creation Date, Modification Date
└── Page Count
↓
Store in results['metadata']
```

**Technical Details**:
- Uses PyMuPDF's `fitz.open()` to access PDF structure
- Metadata stored in standard PDF dictionary format
- Dates in PDF date format: `D:YYYYMMDDHHmmSS`

### 3. Text Extraction Pipeline

#### Method A: Enhanced Extraction (pymupdf4llm)
```
For each page in PDF:
├── pymupdf4llm.get_page_markdown(doc, page_num)
├── Analyzes text blocks, fonts, positions
├── Identifies headings, paragraphs, lists
├── Preserves formatting with markdown syntax
└── Returns structured markdown text
```

**Advantages**:
- Maintains document hierarchy (H1, H2, lists)
- Better handling of multi-column layouts
- Preserves text styling (bold, italic via markdown)
- Ideal for LLM processing

#### Method B: Standard Extraction (PyMuPDF)
```
For each page in PDF:
├── page.get_text()
├── Extracts text in reading order
├── Raw text with basic spacing
└── Returns plain text string
```

**Fallback Trigger**: If pymupdf4llm unavailable or extraction fails

### 4. Table Extraction Mechanism

```
pdfplumber opens PDF:
├── For each page:
│   ├── Detect table boundaries via line detection
│   ├── Identify cell structures and borders
│   ├── Extract cell contents
│   ├── Build 2D array structure
│   └── Convert to pandas DataFrame
│       ├── First row → Column headers
│       └── Remaining rows → Data
└── Store with metadata (page, table_num)
```

**Technical Approach**:
- Uses visual line detection algorithms
- Identifies table structures from PDF drawing commands
- Handles merged cells and complex layouts
- Exports to CSV for universal compatibility

### 5. Image Extraction Strategies

#### Strategy A: High-Quality (pdf2image)
```
convert_from_path(pdf_path):
├── Poppler converts each page to high-res image
├── DPI: 300 (configurable)
├── Format: PIL Image objects
└── Returns list of images (one per page)
```

**Technical Details**:
- Uses Poppler's rendering engine
- Captures exact visual appearance
- Includes all graphical elements
- Memory intensive (300 DPI = ~25MB per page)

#### Strategy B: Fallback (PyMuPDF)
```
For each page:
├── page.get_pixmap(dpi=300)
├── PyMuPDF renders page to pixmap
├── Convert pixmap to PNG bytes
├── PIL.Image.open() from bytes
└── Return PIL Image object
```

**Differences from pdf2image**:
- Slightly lower quality rendering
- No external dependencies
- Faster for simple PDFs

### 6. OCR Processing Flow

#### Engine A: PyMuPDF Built-in OCR
```
For each page pixmap:
├── Check TESSDATA_PREFIX environment variable
├── pix.pdfocr_tobytes() → Create OCR-embedded PDF
├── Open OCR PDF as fitz.Document
├── Extract text from OCR layer
└── Return OCR text string
```

**Requirements**:
- `TESSDATA_PREFIX` environment variable set
- Tesseract language data files installed
- No Python package dependencies

#### Engine B: Pytesseract
```
For each page image:
├── pytesseract.image_to_string(image)
├── Tesseract analyzes image pixels
├── Identifies text regions and characters
├── Returns recognized text
└── Store with page number
```

**Requirements**:
- `pytesseract` Python package
- Tesseract OCR binary installed on system

### 7. Results Aggregation & Storage

```
save_results(results, output_dir):
├── Create output directory structure:
│   ├── metadata.txt
│   ├── extracted_text.txt
│   ├── tables/
│   │   ├── page_1_table_1.csv
│   │   └── page_2_table_1.csv
│   ├── images/
│   │   ├── page_1.png
│   │   └── page_2.png
│   └── ocr_text.txt
└── Compress to ZIP for download
```

### 8. Error Handling & Fallbacks

The system implements multiple fallback layers:

```
Text Extraction:
pymupdf4llm → PyMuPDF standard → Empty list

Image Extraction:
pdf2image → PyMuPDF pixmap → Empty list

OCR:
pytesseract → PyMuPDF OCR → No OCR (graceful)

Table Extraction:
pdfplumber → Warning log → Empty list
```

## 📋 Requirements

### Core Dependencies (Required)
- **Python 3.7+**
- **streamlit**: Web UI framework
- **PyMuPDF (fitz)**: Core PDF processing
- **pdfplumber**: Table extraction
- **Pillow (PIL)**: Image processing
- **pandas**: Data manipulation
- **python-dateutil**: Date parsing

### Optional Dependencies (Enhanced Features)

#### For Enhanced Text Extraction
- **pymupdf4llm**: Markdown-formatted text extraction with layout intelligence

#### For High-Quality Images
- **pdf2image**: Superior image rendering
- **Poppler**: System-level PDF rendering (required by pdf2image)
  - Windows: [Download Poppler](https://github.com/oschwartz10612/poppler-windows/releases/)
  - Linux: `apt-get install poppler-utils`
  - macOS: `brew install poppler`

#### For OCR Functionality
- **pytesseract**: Python wrapper for Tesseract
- **Tesseract OCR**: System-level OCR engine
  - Windows: [Download Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`

**OR**

- **TESSDATA_PREFIX Environment Variable**: For PyMuPDF's built-in OCR
  ```bash
  # Windows
  set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
  
  # Linux/macOS
  export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
  ```

## 🚀 Installation

### Method 1: Standard Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/Rhushya/PDF_parser
cd PDF_parser

# Install core dependencies
pip install -r requirements.txt
```

### Method 2: Full Installation (All Features)

```bash
# Install core dependencies
pip install -r requirements.txt

# Install optional dependencies
pip install pdf2image pytesseract pymupdf4llm

# Install system dependencies (choose your OS)

# Windows (using Chocolatey)
choco install poppler tesseract

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr

# macOS
brew install poppler tesseract
```

### Method 3: Conda Environment (Isolated)

```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate environment
conda activate pdf_parser

# Install system dependencies separately (see Method 2)
```

## 🎮 Usage

### Running the Application

```bash
# Start the Streamlit server
streamlit run app.py

# Alternative: Use run.py wrapper
python run.py
```

The application will launch at `http://localhost:8501` in your default browser.

### Using the Interface

1. **Upload PDF**: Click "Browse files" or drag-and-drop a PDF
2. **Processing**: Wait for automatic extraction (progress indicator shows status)
3. **View Results**: Navigate through tabs:
   - **Metadata**: Document properties
   - **Text**: Extracted text with page markers
   - **Tables**: Interactive DataFrames with CSV download
   - **Images & OCR**: Side-by-side images and OCR text
4. **Download**: 
   - Individual items: Click download buttons in each tab
   - All content: Use "Download All Results" ZIP button

### Programmatic Usage

```python
from utils.pdf_parser import PDFParser

# Initialize parser
parser = PDFParser()

# Process PDF
results = parser.process_pdf('path/to/document.pdf')

# Access results
print(f"Pages: {results['metadata']['pages']}")
print(f"Text blocks: {len(results['text'])}")
print(f"Tables found: {len(results['tables'])}")
print(f"Images extracted: {len(results['images'])}")

# Save to directory
parser.save_results(results, 'output_directory/')
```

## 🔧 Configuration

### Environment Variables

```bash
# For PyMuPDF OCR
TESSDATA_PREFIX=/path/to/tessdata

# For custom Tesseract binary location
TESSERACT_CMD=/usr/local/bin/tesseract
```

### Streamlit Configuration (Optional)

Create `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 200  # Max file size in MB

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F0F0"
```

## 🧪 Dependency Verification

The application automatically checks dependencies on startup:

- ✅ **Green**: Optional dependency available, enhanced features enabled
- ℹ️ **Blue**: Using fallback method, core features functional
- ⚠️ **Yellow**: Optional feature disabled, configuration needed

### Checking Your Installation

```python
# In Python console
from utils.pdf_parser import PDFParser

parser = PDFParser()
# Check console output for dependency status:
# - "pymupdf4llm is available" → Enhanced text extraction enabled
# - "pdf2image not available" → Using PyMuPDF fallback
# - "PyMuPDF OCR is not available" → pytesseract or config needed
```

## 📊 Performance Considerations

### Memory Usage
- **Text/Metadata**: Minimal (<5MB per document)
- **Tables**: ~1-5MB depending on table size
- **Images (300 DPI)**: ~25-50MB per page
- **Recommendation**: 8GB RAM for documents <100 pages

### Processing Time (estimates)
- **10-page document**: 5-15 seconds
- **50-page document**: 30-60 seconds
- **100-page document**: 1-3 minutes

**Bottlenecks**:
- OCR: Most time-intensive (2-5 seconds per page)
- High-res image extraction: 1-2 seconds per page
- Tables: 0.5-1 second per page

### Optimization Tips
1. Disable OCR if not needed (faster processing)
2. Use PyMuPDF image fallback for previews
3. Process large documents in batches
4. Use SSD storage for temporary files

## 🐛 Troubleshooting

### Issue: "No OCR support: TESSDATA_PREFIX not set"

**Solution**:
```bash
# Find tessdata location
# Windows: Usually C:\Program Files\Tesseract-OCR\tessdata
# Linux: /usr/share/tesseract-ocr/*/tessdata

# Set environment variable (adjust path)
set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata  # Windows
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata  # Linux

# Restart application
```

### Issue: "pdf2image requires Poppler"

**Solution**: Install Poppler system library:
- Windows: Download from [Poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/), add `bin/` to PATH
- Linux: `sudo apt-get install poppler-utils`
- macOS: `brew install poppler`

### Issue: "No tables detected" (but tables exist)

**Possible Causes**:
- Tables without borders (use OCR on images instead)
- Complex table layouts (manual extraction needed)
- Scanned PDFs (text not searchable)

### Issue: "Memory error on large PDFs"

**Solutions**:
1. Process pages in batches
2. Reduce image DPI (modify code: `dpi=150` instead of 300)
3. Disable image extraction for text-only needs
4. Increase system RAM or use swap

## 📁 Project Structure

```
PDF_parser/
│
├── app.py                      # Streamlit web application
├── run.py                      # Application launcher script
├── requirements.txt            # Python dependencies
├── environment.yml             # Conda environment spec
├── README.md                   # This file
│
├── utils/
│   ├── __init__.py
│   └── pdf_parser.py           # Core PDF extraction engine
│
└── example/
    └── pdf_parser_final.ipynb  # Jupyter notebook demonstration
```

## 🔐 Privacy & Security

- **No Data Storage**: All processing happens locally; no data sent to external servers
- **Temporary Files**: Automatically cleaned up after processing
- **No Tracking**: No analytics or telemetry
- **Open Source**: Full code transparency

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Support for password-protected PDFs
- Batch processing multiple PDFs
- Advanced table detection for borderless tables
- Custom OCR language selection
- PDF form field extraction

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Poppler](https://poppler.freedesktop.org/)

---

## 📝 Prompt for Using in Other Tools

**Copy this prompt to use the working methodology in other projects:**

```
I need a PDF content extraction system with the following architecture:

CORE FUNCTIONALITY:
1. Metadata extraction using PyMuPDF (fitz) - extract all PDF properties
2. Text extraction with fallback mechanism:
   - Primary: pymupdf4llm for markdown-formatted text with layout preservation
   - Fallback: Standard PyMuPDF text extraction
3. Table detection and extraction using pdfplumber, converted to pandas DataFrames
4. Image extraction with dual strategy:
   - Primary: pdf2image with Poppler (300 DPI, high quality)
   - Fallback: PyMuPDF pixmap rendering
5. OCR processing with dual engine support:
   - Primary: pytesseract with Tesseract OCR
   - Fallback: PyMuPDF built-in OCR (requires TESSDATA_PREFIX)

TECHNICAL REQUIREMENTS:
- Implement adaptive dependency checking (work without optional libraries)
- Use temporary directories for isolated processing
- Provide comprehensive error handling with graceful fallbacks
- Structure results as dictionary with keys: metadata, text, tables, images, ocr_text
- Each extracted item includes page number for traceability
- Implement save_results() method for exporting to filesystem

ARCHITECTURE PATTERN:
- Core engine class (PDFParser) with modular extraction methods
- Dependency detection in __init__() with HAS_* flags
- Private methods (_method_name) for internal fallback strategies
- Public methods for main operations (process_pdf, save_results)
- Logging for warnings/errors without stopping execution

ERROR HANDLING STRATEGY:
- Try primary method → catch exception → try fallback → log warning if fails
- Never raise exceptions for partial failures (missing tables, OCR failures)
- Only raise for critical failures (file not found, corrupt PDF)

OUTPUT STRUCTURE:
{
    'metadata': {...},  # All PDF properties
    'text': [{'page': 1, 'content': '...'}, ...],
    'tables': [{'page': 1, 'table_num': 1, 'dataframe': df}, ...],
    'images': [{'page': 1, 'image': PIL.Image}, ...],
    'ocr_text': [{'page': 1, 'content': '...'}, ...]
}

DEPENDENCIES:
Core: PyMuPDF, pdfplumber, Pillow, pandas
Optional: pymupdf4llm, pdf2image, pytesseract

Implement this architecture with clear separation of concerns, comprehensive logging, and user-friendly error messages for missing dependencies.
```

---

**Version**: 1.0.0  
**Last Updated**: January 3, 2026  
**Author**: Rhushya  
**Repository**: https://github.com/Rhushya/PDF_parser