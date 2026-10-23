try:
    import pymupdf as fitz
except ImportError:
    import fitz
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_with_ocr(file_path: str) -> str:
    """
    Renders PDF pages as high-DPI images and uses Tesseract OCR to extract text.
    Used as fallback when normal PDF text extraction yields little to no text.
    """
    try:
        import pytesseract
    except ImportError:
        logger.warning("pytesseract is not installed.")
        return ""

    extracted_pages = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render page at 200 DPI for clear OCR
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            
            try:
                ocr_text = pytesseract.image_to_string(img)
                if ocr_text:
                    extracted_pages.append(ocr_text.strip())
            except Exception as ocr_err:
                logger.error(f"Tesseract OCR failed on page {page_num}: {str(ocr_err)}")
                
        doc.close()
    except Exception as e:
        logger.error(f"Failed rendering PDF for OCR: {str(e)}")
        
    return "\n\n".join(extracted_pages).strip()
