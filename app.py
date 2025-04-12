import streamlit as st
import os
import tempfile
from utils.pdf_parser import PDFParser
import pandas as pd
import glob
import shutil
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="PDF Parser",
    page_icon="📄",
    layout="wide"
)

# Initialize the PDF parser
@st.cache_resource
def get_parser():
    return PDFParser()

parser = get_parser()

st.title("📄 PDF Parser")
st.write("Upload PDF documents to extract text, tables, and images.")

# Check for common dependencies
try:
    from pdf2image import convert_from_path
    has_pdf2image = True
except (ImportError, ModuleNotFoundError):
    has_pdf2image = False

try:
    import pytesseract
    has_pytesseract = True
except (ImportError, ModuleNotFoundError):
    has_pytesseract = False

# Display installation instructions if dependencies are missing
if not has_pdf2image:
    st.warning("""
    ⚠️ pdf2image is not installed or Poppler is missing. 
    The app will fallback to PyMuPDF for image extraction, but quality may be reduced.
    
    To install pdf2image: `pip install pdf2image`
    
    For Poppler:
    - Windows: Download from [here](https://github.com/oschwartz10612/poppler-windows/releases/)
      and add the bin folder to your PATH.
    - MacOS: `brew install poppler`
    - Linux: `apt-get install poppler-utils`
    """)

if not has_pytesseract:
    st.warning("""
    ⚠️ pytesseract is not installed or Tesseract OCR is missing.
    OCR functionality will be disabled.
    
    To install pytesseract: `pip install pytesseract`
    
    For Tesseract OCR:
    - Windows: Download from [here](https://github.com/UB-Mannheim/tesseract/wiki)
      and add it to your PATH.
    - MacOS: `brew install tesseract`
    - Linux: `apt-get install tesseract-ocr`
    """)

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])

if uploaded_file is not None:
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(pdf_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Process PDF
        with st.spinner("Processing PDF..."):
            try:
                results = parser.process_pdf(pdf_path)
                
                # Save results to a temporary directory
                output_dir = os.path.join(temp_dir, 'output')
                parser.save_results(results, output_dir)
                
                # Display results in tabs
                tab1, tab2, tab3, tab4 = st.tabs(["Metadata", "Text", "Tables", "Images & OCR"])
                
                with tab1:
                    st.header("Document Metadata")
                    metadata_df = pd.DataFrame.from_dict(results['metadata'], orient='index', columns=['Value'])
                    metadata_df.index.name = 'Property'
                    st.dataframe(metadata_df, use_container_width=True)
                
                with tab2:
                    st.header("Extracted Text")
                    if results['text']:
                        for text_item in results['text']:
                            with st.expander(f"Page {text_item['page']}"):
                                st.text(text_item['content'])
                    else:
                        st.info("No text was extracted from the document.")
                
                with tab3:
                    st.header("Extracted Tables")
                    if results['tables']:
                        for table in results['tables']:
                            with st.expander(f"Page {table['page']} - Table {table['table_num']}"):
                                st.dataframe(table['dataframe'], use_container_width=True)
                                
                                # Download button for CSV
                                csv_path = os.path.join(output_dir, 'tables', f"page_{table['page']}_table_{table['table_num']}.csv")
                                if os.path.exists(csv_path):
                                    with open(csv_path, 'rb') as f:
                                        st.download_button(
                                            label="Download CSV",
                                            data=f,
                                            file_name=f"table_page{table['page']}_table{table['table_num']}.csv",
                                            mime="text/csv"
                                        )
                    else:
                        st.info("No tables found in the document.")
                
                with tab4:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.header("Images")
                        if results['images']:
                            for img_item in results['images']:
                                with st.expander(f"Page {img_item['page']}"):
                                    st.image(img_item['image'], use_column_width=True)
                        else:
                            st.info("No images were extracted from the document.")
                    
                    with col2:
                        st.header("OCR Text")
                        if results['ocr_text']:
                            for ocr_item in results['ocr_text']:
                                with st.expander(f"Page {ocr_item['page']}"):
                                    st.text(ocr_item['content'])
                        else:
                            if not has_pytesseract:
                                st.info("OCR is disabled because pytesseract is not installed.")
                            else:
                                st.info("No OCR text was extracted.")
                
                # Add download buttons for all extracted content
                if any([results['text'], results['tables'], results['images'], results['ocr_text']]):
                    st.header("Download Results")
                    
                    # Create a zip file containing all results
                    results_zip = shutil.make_archive(
                        os.path.join(temp_dir, 'results'), 
                        'zip', 
                        output_dir
                    )
                    
                    with open(results_zip, 'rb') as f:
                        st.download_button(
                            label="Download All Results",
                            data=f,
                            file_name=f"{Path(uploaded_file.name).stem}_results.zip",
                            mime="application/zip"
                        )
                    
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
                st.error("Please make sure all dependencies are installed properly.")
else:
    st.info("Please upload a PDF file to begin.")

# Add footer with instructions
st.markdown("---")
st.markdown("""
### How to use this app:
1. Upload a PDF file using the file uploader
2. Wait for the processing to complete
3. Explore the extracted content in the tabs
4. Download individual tables or all results as a ZIP file

### Dependencies:
- For image extraction: pdf2image and Poppler
- For OCR: pytesseract and Tesseract OCR
""")

# Display app information
with st.sidebar:
    st.header("About")
    st.info("""
    This app extracts content from PDF files:
    
    - Document metadata
    - Text content
    - Tables (converted to dataframes)
    - Images
    - OCR text from images
    
    No data is stored on servers; all processing happens in your browser.
    """)
    
    st.header("Troubleshooting")
    with st.expander("Missing Dependencies"):
        st.markdown("""
        ### Installing Poppler:
        
        **Windows:**
        1. Download from [GitHub](https://github.com/oschwartz10612/poppler-windows/releases/)
        2. Extract to a folder (e.g., `C:\\Program Files\\poppler`)
        3. Add the `bin` folder to your PATH
        
        **Mac:**
        ```
        brew install poppler
        ```
        
        **Linux:**
        ```
        apt-get install poppler-utils
        ```
        
        ### Installing Tesseract:
        
        **Windows:**
        1. Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
        2. Run installer and add to PATH
        
        **Mac:**
        ```
        brew install tesseract
        ```
        
        **Linux:**
        ```
        apt-get install tesseract-ocr
        ```
        """)
