import difflib
import logging
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder

logger = logging.getLogger(__name__)

class VerificationService:
    """
    Core verification engine for CortexGrid:
    1. Duplicate Invoice Detection
    2. Intelligent Vendor Matching (with confidence & ambiguity handling)
    3. Purchase Order Comparison
    """

    @staticmethod
    def verify_invoice(invoice: Invoice) -> dict:
        """
        Runs full verification suite against an invoice and updates its fields.
        Returns a verification summary dict.
        """
        results = {
            "duplicate": VerificationService.check_duplicate(invoice),
            "vendor_match": VerificationService.match_vendor(invoice),
            "po_verification": VerificationService.verify_purchase_order(invoice)
        }
        return results

    @staticmethod
    def check_duplicate(invoice: Invoice) -> dict:
        """
        Checks if an invoice with the same invoice_number already exists in the database.
        """
        if not invoice.invoice_number or invoice.invoice_number in ['Pending Extraction', 'N/A']:
            invoice.is_duplicate = False
            invoice.duplicate_of_id = None
            return {"is_duplicate": False, "message": "No invoice number available to evaluate duplicates."}

        # Query existing completed or uploaded invoices with same invoice_number
        existing_matches = Invoice.query.filter(
            Invoice.invoice_number.ilike(invoice.invoice_number.strip()),
            Invoice.id != invoice.id
        ).all()

        if not existing_matches:
            invoice.is_duplicate = False
            invoice.duplicate_of_id = None
            return {"is_duplicate": False, "message": "No duplicate invoice number detected in repository."}

        # Candidate duplicate found
        duplicate = existing_matches[0]
        invoice.is_duplicate = True
        invoice.duplicate_of_id = duplicate.id

        vendor_detail = f" from vendor '{duplicate.vendor.name}'" if duplicate.vendor else ""
        date_detail = f" on {duplicate.invoice_date}" if duplicate.invoice_date else ""
        explanation = (
            f"Possible duplicate invoice detected! Matches existing Invoice #{duplicate.id} "
            f"({duplicate.invoice_number}){vendor_detail}{date_detail}."
        )

        logger.warning(f"Duplicate detected: Invoice {invoice.id} duplicates {duplicate.id}")
        return {
            "is_duplicate": True,
            "duplicate_of_id": duplicate.id,
            "message": explanation
        }

    @staticmethod
    def match_vendor(invoice: Invoice) -> dict:
        """
        Compares extracted vendor name against registered vendors using text similarity.
        High confidence (>= 0.85): Automatically links vendor.
        Ambiguous (0.50 - 0.84): Proposes candidate without automatic linking.
        Unmatched (< 0.50): Flags as unrecognized vendor.
        """
        raw_name = invoice.raw_vendor_name
        if not raw_name:
            invoice.vendor_match_status = 'unmatched'
            invoice.vendor_match_score = 0.0
            return {
                "status": "unmatched",
                "score": 0.0,
                "matched_vendor_id": None,
                "message": "No vendor name could be extracted from document text."
            }

        norm_extracted = Vendor.normalize(raw_name)
        vendors = Vendor.query.all()

        best_vendor = None
        best_score = 0.0

        for v in vendors:
            # Direct exact normalized match
            if v.normalized_name == norm_extracted:
                best_vendor = v
                best_score = 1.0
                break

            # SequenceMatcher ratio
            ratio = difflib.SequenceMatcher(None, norm_extracted, v.normalized_name).ratio()
            # Token set check
            words_v = set(v.normalized_name.split())
            words_ext = set(norm_extracted.split())
            if words_v and words_ext:
                token_overlap = len(words_v.intersection(words_ext)) / max(len(words_v), len(words_ext))
                ratio = max(ratio, token_overlap)

            if ratio > best_score:
                best_score = ratio
                best_vendor = v

        invoice.vendor_match_score = round(best_score, 2)

        if best_score >= 0.85 and best_vendor:
            invoice.vendor_id = best_vendor.id
            invoice.vendor_match_status = 'matched'
            msg = f"Confirmed match with registered vendor '{best_vendor.name}' (Confidence: {int(best_score*100)}%)."
            return {"status": "matched", "score": best_score, "matched_vendor_id": best_vendor.id, "vendor_name": best_vendor.name, "message": msg}

        elif best_score >= 0.50 and best_vendor:
            # Ambiguous: do NOT auto-assign vendor_id to avoid incorrect linking
            invoice.vendor_match_status = 'ambiguous'
            msg = f"Ambiguous vendor match. Candidate: '{best_vendor.name}' (Confidence: {int(best_score*100)}%). Finance user verification required."
            return {"status": "ambiguous", "score": best_score, "candidate_vendor_id": best_vendor.id, "candidate_name": best_vendor.name, "message": msg}

        else:
            invoice.vendor_match_status = 'unmatched'
            msg = f"Extracted vendor '{raw_name}' is not registered in the system."
            return {"status": "unmatched", "score": best_score, "matched_vendor_id": None, "message": msg}

    @staticmethod
    def verify_purchase_order(invoice: Invoice) -> dict:
        """
        Compares invoice totals against linked Purchase Order or attempts to auto-link by PO number.
        """
        po = None

        # 1. Use explicitly linked PO if present
        if invoice.purchase_order_id:
            po = PurchaseOrder.query.get(invoice.purchase_order_id)

        # 2. Else attempt to auto-link by extracted po_number
        elif invoice.po_number:
            po = PurchaseOrder.query.filter(PurchaseOrder.po_number.ilike(invoice.po_number.strip())).first()
            if po:
                invoice.purchase_order_id = po.id

        if not po:
            invoice.po_match_status = 'missing'
            invoice.po_amount_diff = 0.0
            return {
                "status": "missing",
                "message": "No linked Purchase Order found for this invoice."
            }

        # Perform amount comparison
        inv_total = invoice.total_amount or 0.0
        po_total = po.total_amount or 0.0
        diff = round(inv_total - po_total, 2)
        invoice.po_amount_diff = diff

        if abs(diff) < 0.01:
            invoice.po_match_status = 'matched'
            msg = f"Invoice total exactly matches Purchase Order {po.po_number} ({po.currency} {po_total:,.2f})."
            return {
                "status": "matched",
                "po_number": po.po_number,
                "po_total": po_total,
                "invoice_total": inv_total,
                "diff": 0.0,
                "message": msg
            }
        else:
            invoice.po_match_status = 'mismatched'
            pct_diff = round((abs(diff) / po_total * 100), 1) if po_total > 0 else 100.0
            direction = "exceeds" if diff > 0 else "is lower than"
            msg = (
                f"Amount mismatch! Invoice total ({invoice.currency} {inv_total:,.2f}) {direction} "
                f"Purchase Order {po.po_number} ({po.currency} {po_total:,.2f}) by "
                f"{invoice.currency} {abs(diff):,.2f} ({pct_diff}% variance)."
            )
            return {
                "status": "mismatched",
                "po_number": po.po_number,
                "po_total": po_total,
                "invoice_total": inv_total,
                "diff": diff,
                "variance_pct": pct_diff,
                "message": msg
            }
