import os
import fitz  # PyMuPDF
import pdfplumber
import io
import pandas as pd
import logging
import sys
from PIL import Image

# Try importing pdf2image and pytesseract, but handle if they're not available
try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except (ImportError, ModuleNotFoundError):
    HAS_PDF2IMAGE = False

try:
    import pytesseract
    HAS_PYTESSERACT = True
except (ImportError, ModuleNotFoundError):
    HAS_PYTESSERACT = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    """Class for extracting text, tables, and images from PDF documents."""
    
    def __init__(self):
        """Initialize the PDF parser."""
        if not HAS_PDF2IMAGE:
            logger.warning("pdf2image not available. Image extraction will use PyMuPDF instead.")
        if not HAS_PYTESSERACT:
            logger.warning("pytesseract not available. OCR functionality will be disabled.")
    
    def _extract_images_pymupdf(self, pdf_doc):
        """Extract images using PyMuPDF as fallback when pdf2image is not available."""
        images = []
        
        for page_idx, page in enumerate(pdf_doc):
            # Get images from the page
            try:
                pix = page.get_pixmap(dpi=300)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                images.append({
                    'page': page_idx + 1,
                    'image': img
                })
            except Exception as e:
                logger.warning(f"Could not extract image from page {page_idx + 1}: {str(e)}")
                
        return images
        
    def process_pdf(self, pdf_path):
        """
        Process a PDF file to extract metadata, text, tables, and images.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            dict: Dictionary containing extracted PDF components.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # Initialize results dictionary
        results = {
            'metadata': {},
            'text': [],
            'tables': [],
            'images': [],
            'ocr_text': []
        }
        
        try:
            # Extract metadata and text using PyMuPDF
            with fitz.open(pdf_path) as doc:
                results['metadata'] = {
                    'title': doc.metadata.get('title', ''),
                    'author': doc.metadata.get('author', ''),
                    'subject': doc.metadata.get('subject', ''),
                    'creator': doc.metadata.get('creator', ''),
                    'producer': doc.metadata.get('producer', ''),
                    'creation_date': doc.metadata.get('creationDate', ''),
                    'modification_date': doc.metadata.get('modDate', ''),
                    'pages': len(doc)
                }
                
                # Extract text using PyMuPDF
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    if text.strip():
                        results['text'].append({
                            'page': page_num + 1,
                            'content': text
                        })
                
                # Extract images using PyMuPDF if pdf2image is not available
                if not HAS_PDF2IMAGE:
                    results['images'] = self._extract_images_pymupdf(doc)
            
            # Extract tables using pdfplumber
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        try:
                            tables = page.extract_tables()
                            for table_num, table in enumerate(tables):
                                if table:  # Skip empty tables
                                    # Convert table to pandas DataFrame
                                    if table[0]:  # If table has headers
                                        df = pd.DataFrame(table[1:], columns=table[0])
                                    else:
                                        df = pd.DataFrame(table)
                                        
                                    results['tables'].append({
                                        'page': page_num + 1,
                                        'table_num': table_num + 1,
                                        'dataframe': df
                                    })
                        except Exception as e:
                            logger.warning(f"Error extracting tables from page {page_num + 1}: {str(e)}")
            except Exception as e:
                logger.warning(f"Error extracting tables: {str(e)}")
            
            # Extract images and perform OCR using pdf2image and pytesseract if available
            if HAS_PDF2IMAGE:
                try:
                    images = convert_from_path(pdf_path)
                    for page_num, image in enumerate(images):
                        # Save image for results
                        results['images'].append({
                            'page': page_num + 1,
                            'image': image
                        })
                        
                        # Perform OCR if pytesseract is available
                        if HAS_PYTESSERACT:
                            try:
                                ocr_text = pytesseract.image_to_string(image)
                                if ocr_text.strip():
                                    results['ocr_text'].append({
                                        'page': page_num + 1,
                                        'content': ocr_text
                                    })
                            except Exception as e:
                                logger.warning(f"OCR failed for page {page_num + 1}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Error extracting images with pdf2image: {str(e)}. Will try PyMuPDF instead.")
                    # If pdf2image fails, try PyMuPDF as fallback for images
                    with fitz.open(pdf_path) as doc:
                        results['images'] = self._extract_images_pymupdf(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise

    def save_results(self, results, output_dir):
        """
        Save the extracted results to the specified output directory.
        
        Args:
            results (dict): Dictionary containing extracted PDF components.
            output_dir (str): Directory where to save the results.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        try:
            # Save metadata
            with open(os.path.join(output_dir, 'metadata.txt'), 'w', encoding='utf-8') as f:
                for key, value in results['metadata'].items():
                    f.write(f"{key}: {value}\n")
            
            # Save extracted text
            if results['text']:
                with open(os.path.join(output_dir, 'extracted_text.txt'), 'w', encoding='utf-8') as f:
                    for text_item in results['text']:
                        f.write(f"=== Page {text_item['page']} ===\n")
                        f.write(text_item['content'])
                        f.write('\n\n')
                    
            # Save tables as CSV files
            if results['tables']:
                tables_dir = os.path.join(output_dir, 'tables')
                os.makedirs(tables_dir, exist_ok=True)
                for table in results['tables']:
                    table_path = os.path.join(tables_dir, f"page_{table['page']}_table_{table['table_num']}.csv")
                    table['dataframe'].to_csv(table_path, index=False)
                
            # Save OCR text
            if results['ocr_text']:
                with open(os.path.join(output_dir, 'ocr_text.txt'), 'w', encoding='utf-8') as f:
                    for ocr_item in results['ocr_text']:
                        f.write(f"=== Page {ocr_item['page']} ===\n")
                        f.write(ocr_item['content'])
                        f.write('\n\n')
                        
            # Save images
            if results['images']:
                images_dir = os.path.join(output_dir, 'images')
                os.makedirs(images_dir, exist_ok=True)
                for img_item in results['images']:
                    img_path = os.path.join(images_dir, f"page_{img_item['page']}.png")
                    img_item['image'].save(img_path)
                
            logger.info(f"Results saved to {output_dir}")
                
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise 