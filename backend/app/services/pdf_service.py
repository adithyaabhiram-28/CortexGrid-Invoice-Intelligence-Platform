try:
    import pymupdf as fitz
except ImportError:
    import fitz
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from all pages of a PDF using PyMuPDF (fitz).
    Returns combined text string.
    """
    extracted_text_pages = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text:
                extracted_text_pages.append(text.strip())
        doc.close()
    except Exception as e:
        logger.error(f"PyMuPDF text extraction failed for {file_path}: {str(e)}")
        
    full_text = "\n\n".join(extracted_text_pages).strip()
    
    # Optional pdfplumber fallback attempt if fitz returned very little text
    if len(full_text.split()) < 15:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                plumber_pages = []
                for p in pdf.pages:
                    p_text = p.extract_text()
                    if p_text:
                        plumber_pages.append(p_text.strip())
                plumber_text = "\n\n".join(plumber_pages).strip()
                if len(plumber_text.split()) > len(full_text.split()):
                    full_text = plumber_text
        except Exception as e:
            logger.warning(f"pdfplumber fallback extraction failed: {str(e)}")
            
    return full_text
