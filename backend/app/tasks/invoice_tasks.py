import logging
import traceback
from app.extensions import db, celery_app
from app.models import Invoice, Vendor
from app.services.storage_service import LocalStorageService
from app.services.pdf_service import extract_text_from_pdf
from app.services.ocr_service import extract_text_with_ocr
from app.services.invoice_parser import parse_invoice_text
from app.services.verification_service import VerificationService
from app.services.risk_service import RiskAssessmentService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

def process_invoice_logic(invoice_id: int):
    """
    End-to-end processing pipeline:
    1. Status -> processing
    2. PyMuPDF text extraction + OCR fallback
    3. Structured regex extraction
    4. Verification: Duplicate detection, Vendor matching, PO comparison
    5. Explainable Risk Assessment
    6. Optional AI Analysis (Gemini)
    7. Status -> completed (or failed on crash)
    """
    invoice = db.session.get(Invoice, invoice_id) if hasattr(db.session, 'get') else Invoice.query.get(invoice_id)
    if not invoice:
        logger.error(f"Invoice with ID {invoice_id} not found.")
        return False

    try:
        # Step 1: Update status to processing
        invoice.processing_status = 'processing'
        invoice.error_message = None
        db.session.commit()

        # Step 2: Locate PDF file
        storage = LocalStorageService()
        file_path = storage.get_file_path(invoice.file_path)

        # Step 3: Extract text (Normal PyMuPDF text extraction)
        extracted_text = extract_text_from_pdf(file_path)

        # Step 4: OCR Fallback if text is sparse (< 30 words)
        word_count = len(extracted_text.split()) if extracted_text else 0
        if word_count < 30:
            logger.info(f"Sparse text ({word_count} words) for invoice {invoice_id}. Attempting OCR fallback...")
            try:
                ocr_text = extract_text_with_ocr(file_path)
                if ocr_text and len(ocr_text.split()) > word_count:
                    extracted_text = ocr_text
            except Exception as ocr_err:
                logger.warning(f"OCR fallback error: {ocr_err}")

        invoice.extracted_text = extracted_text

        # Step 5: Structured Data Extraction (Regex parsing)
        parsed_data = parse_invoice_text(extracted_text)

        if parsed_data.get('invoice_number'):
            invoice.invoice_number = parsed_data['invoice_number']
        if parsed_data.get('invoice_date'):
            invoice.invoice_date = parsed_data['invoice_date']
        if parsed_data.get('po_number'):
            invoice.po_number = parsed_data['po_number']
        if parsed_data.get('total_amount') is not None:
            invoice.total_amount = parsed_data['total_amount']
        if parsed_data.get('currency'):
            invoice.currency = parsed_data['currency']

        # Store raw extracted vendor name
        if parsed_data.get('vendor_name'):
            invoice.raw_vendor_name = parsed_data['vendor_name']

        invoice.extraction_confidence = parsed_data.get('confidence', 0.0)

        # Step 6: Verification Layer (Duplicate detection, Vendor matching, PO check)
        VerificationService.verify_invoice(invoice)

        # Step 7: Explainable Risk Assessment
        RiskAssessmentService.evaluate(invoice)

        # Step 8: Optional AI Document Intelligence (Gemini)
        if AIService.is_available():
            try:
                ai_result = AIService.analyze_invoice(invoice.to_dict(), extracted_text)
                if ai_result.get('available') and ai_result.get('summary'):
                    invoice.ai_summary = ai_result.get('summary')
            except Exception as ai_err:
                logger.warning(f"Optional AI analysis skipped: {ai_err}")

        # Check for incomplete extraction notice (without failing the entire run)
        missing = parsed_data.get('missing_fields', [])
        if missing and not invoice.error_message:
            missing_labels = ", ".join(f.replace('_', ' ') for f in missing)
            invoice.error_message = f"Notice: Incomplete field extraction ({missing_labels} could not be determined)."

        # Step 9: Update status to completed
        invoice.processing_status = 'completed'
        db.session.commit()
        logger.info(f"Successfully processed invoice #{invoice_id}: Status={invoice.processing_status}, Risk={invoice.risk_level} ({invoice.risk_score})")
        return True

    except Exception as e:
        error_msg = f"{str(e)}"
        logger.error(f"Error processing invoice {invoice_id}: {error_msg}\n{traceback.format_exc()}")
        db.session.rollback()

        # Mark as failed with clean message
        try:
            inv = db.session.get(Invoice, invoice_id) if hasattr(db.session, 'get') else Invoice.query.get(invoice_id)
            if inv:
                inv.processing_status = 'failed'
                inv.error_message = error_msg
                db.session.commit()
        except Exception as db_err:
            logger.critical(f"Could not persist failure status for invoice {invoice_id}: {str(db_err)}")
        return False

@celery_app.task(name="process_invoice_task", bind=True)
def process_invoice_task(self, invoice_id: int):
    return process_invoice_logic(invoice_id)
