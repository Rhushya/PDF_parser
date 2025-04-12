import streamlit as st
import os
import tempfile
from utils.pdf_parser import PDFParser
import pandas as pd
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

# Check for optional dependencies
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

try:
    import pymupdf4llm
    has_pymupdf4llm = True
except (ImportError, ModuleNotFoundError):
    has_pymupdf4llm = False

# Simple notification about missing dependencies
if not has_pdf2image:
    st.info("Note: Using fallback image extraction method. For better quality, install pdf2image and Poppler.")

if not has_pytesseract:
    st.info("Note: Using PyMuPDF's built-in OCR instead of pytesseract. This requires the TESSDATA_PREFIX environment variable to be set.")
    # Add a configuration section for OCR if needed
    with st.expander("OCR Configuration"):
        st.markdown("""
        ### Setting up PyMuPDF OCR
        
        For OCR to work with PyMuPDF, set the `TESSDATA_PREFIX` environment variable to the path where Tesseract language data is located.
        
        **Example on Windows:**
        ```
        set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
        ```
        
        **Example on Linux/macOS:**
        ```
        export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
        ```
        
        Restart the application after setting the environment variable.
        """)

if has_pymupdf4llm:
    st.success("Enhanced text extraction with PyMuPDF4LLM is enabled. This provides better formatted text extraction, especially for complex PDF layouts.")

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
                        if has_pymupdf4llm:
                            st.success("Text extracted using enhanced PyMuPDF4LLM for better formatting and layout preservation.")
                        
                        st.info(f"Showing all extracted text from {len(results['text'])} pages")
                        
                        # Display all pages in a single scrollable container with page separators
                        all_text = ""
                        for i, text_item in enumerate(results['text']):
                            all_text += f"--- PAGE {text_item['page']} ---\n\n"
                            all_text += text_item['content']
                            all_text += "\n\n"
                        
                        st.text_area(
                            label="All Text Content",
                            value=all_text,
                            height=600,
                            key="all_text_content"
                        )
                        
                        # Add a download button for all text
                        st.download_button(
                            label="Download All Text",
                            data=all_text,
                            file_name="all_text.txt",
                            mime="text/plain"
                        )
                    else:
                        st.info("No text was extracted from the document.")
                
                with tab3:
                    st.header("Extracted Tables")
                    if results['tables']:
                        st.info(f"Showing all extracted tables ({len(results['tables'])} tables found)")
                        
                        # Display all tables with separators
                        for i, table in enumerate(results['tables']):
                            st.markdown(f"### Page {table['page']} - Table {table['table_num']}")
                            st.dataframe(table['dataframe'], use_container_width=True)
                            
                            # Download button for each table's CSV
                            csv_path = os.path.join(output_dir, 'tables', f"page_{table['page']}_table_{table['table_num']}.csv")
                            if os.path.exists(csv_path):
                                with open(csv_path, 'rb') as f:
                                    st.download_button(
                                        label=f"Download Table {i+1} as CSV",
                                        data=f,
                                        file_name=f"page{table['page']}_table{table['table_num']}.csv",
                                        mime="text/csv",
                                        key=f"download_table_{i}"
                                    )
                            st.markdown("---")
                    else:
                        st.info("No tables found in the document.")
                
                with tab4:
                    st.header("Images & OCR Text")
                    
                    if results['images'] or results['ocr_text']:
                        # Create columns for images and OCR text
                        col1, col2 = st.columns(2)
                        
                        # Handle images
                        with col1:
                            st.subheader("Images")
                            if results['images']:
                                st.info(f"Showing all extracted images ({len(results['images'])} images found)")
                                
                                # Display all images with captions
                                for i, img_item in enumerate(results['images']):
                                    st.image(img_item['image'], use_column_width=True, 
                                             caption=f"Page {img_item['page']} - Image {i+1}")
                                    st.markdown("---")
                            else:
                                st.info("No images were extracted from the document.")
                        
                        # Handle OCR text
                        with col2:
                            st.subheader("OCR Text")
                            if results['ocr_text']:
                                if parser.has_pymupdf_ocr:
                                    st.success("OCR performed using PyMuPDF's built-in OCR engine.")
                                else:
                                    st.info("OCR performed using pytesseract.")
                                
                                st.info(f"Showing all OCR text ({len(results['ocr_text'])} pages)")
                                
                                # Combine all OCR text with page separators
                                all_ocr = ""
                                for i, ocr_item in enumerate(results['ocr_text']):
                                    all_ocr += f"--- PAGE {ocr_item['page']} OCR TEXT ---\n\n"
                                    all_ocr += ocr_item['content']
                                    all_ocr += "\n\n"
                                
                                st.text_area(
                                    label="All OCR Content",
                                    value=all_ocr,
                                    height=600,
                                    key="all_ocr_content"
                                )
                                
                                # Add a download button for all OCR text
                                st.download_button(
                                    label="Download All OCR Text",
                                    data=all_ocr,
                                    file_name="all_ocr_text.txt",
                                    mime="text/plain"
                                )
                            else:
                                if not has_pytesseract and not parser.has_pymupdf_ocr:
                                    st.warning("""
                                    OCR is disabled because neither pytesseract nor PyMuPDF OCR is properly configured.
                                    
                                    To enable OCR:
                                    1. Install pytesseract: `pip install pytesseract` and install Tesseract OCR
                                    OR
                                    2. Set the TESSDATA_PREFIX environment variable for PyMuPDF OCR
                                    """)
                                else:
                                    st.info("No OCR text was extracted from this document.")
                    else:
                        st.info("No images or OCR text were extracted from the document.")
                
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
3. Navigate through the content using the tabs
4. Scroll through all extracted content
5. Download individual items or all results as a ZIP file
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

    # Add OCR information section
    st.header("OCR Information")
    st.info("""
    This app supports two OCR methods:
    
    1. PyMuPDF's built-in OCR (recommended)
       - Requires TESSDATA_PREFIX environment variable
       - More efficient and integrated
    
    2. Pytesseract (fallback)
       - Requires pytesseract and Tesseract OCR installed
       
    At least one of these methods must be configured for OCR to work.
    """)
    
    # Add text extraction information
    st.header("Text Extraction")
    st.info("""
    This app uses advanced text extraction methods:
    
    1. PyMuPDF4LLM (preferred)
       - Better formatting and layout preservation
       - Markdown-formatted text for better readability
       - Improved handling of complex documents
       
    2. Standard PyMuPDF (fallback)
       - Basic text extraction
       
    The app automatically uses the best available method.
    """)
