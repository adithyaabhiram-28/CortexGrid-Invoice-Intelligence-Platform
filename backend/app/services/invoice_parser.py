import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InvoiceParser:
    """
    Enhanced regex and heuristic parser for extracting structured invoice fields.
    Extracts invoice numbers, dates, vendor names, PO numbers, totals, and currencies.
    Calculates extraction confidence and identifies missing fields.
    """
    def parse(self, text: str) -> dict:
        if not text:
            return {
                "invoice_number": None,
                "vendor_name": None,
                "invoice_date": None,
                "po_number": None,
                "total_amount": None,
                "currency": "INR",
                "confidence": 0.0,
                "missing_fields": ["invoice_number", "vendor_name", "invoice_date", "total_amount"]
            }

        invoice_number = self._extract_invoice_number(text)
        vendor_name = self._extract_vendor_name(text)
        invoice_date = self._extract_invoice_date(text)
        po_number = self._extract_po_number(text)
        total_amount, currency = self._extract_total_amount(text)

        missing_fields = []
        if not invoice_number:
            missing_fields.append("invoice_number")
        if not vendor_name:
            missing_fields.append("vendor_name")
        if not invoice_date:
            missing_fields.append("invoice_date")
        if total_amount is None:
            missing_fields.append("total_amount")

        # Confidence: each core field contributes 25%
        confidence = (4 - len(missing_fields)) * 0.25

        return {
            "invoice_number": invoice_number,
            "vendor_name": vendor_name,
            "invoice_date": invoice_date,
            "po_number": po_number,
            "total_amount": total_amount,
            "currency": currency,
            "confidence": confidence,
            "missing_fields": missing_fields
        }

    def _extract_invoice_number(self, text: str):
        patterns = [
            r'\b(INV[-_/][0-9A-Za-z-]+)\b',
            r'\b(BILL[-_/][0-9A-Za-z-]+)\b',
            r'(?:Invoice\s*(?:No|Num|Number|#)|Bill\s*(?:No|Num|Number|#)|Invoice\s*ID|Tax\s*Invoice\s*No)\s*[:.-]?\s*([A-Za-z0-9-_/]+)',
            r'(?:Ref\s*(?:No|#)|Reference\s*ID)\s*[:.-]?\s*([A-Za-z0-9-_/]+)',
            r'(?:Invoice|Bill)\s*[:.-]\s*([A-Za-z0-9-_/]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                inv_num = match.group(1).strip()
                # Exclude false positives
                if len(inv_num) >= 2 and not inv_num.lower() in ['date', 'total', 'no', 'number', 'oice', 'due']:
                    return inv_num
        return None

    def _extract_vendor_name(self, text: str):
        patterns = [
            r'(?:Vendor|Supplier|From|Billed By|Sold By|Company)\s*[:.-]?\s*([A-Za-z0-9\s&.,\'"-]+?)(?=\n|Date|Invoice|Bill|To|GSTIN|CIN|Tax|$)',
            r'^(?:[A-Z0-9\s&.,\'"-]{3,45})(?=\n(?:Inc|Ltd|LLC|Pvt|Corp|Technologies|Solutions|Computers|Services|Systems))',
            r'([A-Za-z0-9\s&.,\'"-]+?\s+(?:Pvt\.?\s*Ltd\.?|Private\s+Limited|Ltd\.?|LLC|Inc\.?|Corporation))'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                vendor = match.group(1).strip()
                # Clean leading punctuation or artifacts
                vendor = re.sub(r'^[^\w]+', '', vendor)
                if 2 < len(vendor) < 80 and not vendor.lower().startswith(('invoice', 'tax', 'bill to', 'ship to')):
                    return vendor
        return None

    def _extract_invoice_date(self, text: str):
        date_patterns = [
            r'(?:Invoice\s*Date|Bill\s*Date|Date\s*of\s*Issue|Date)\s*[:.-]?\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})', # YYYY-MM-DD
            r'(?:Invoice\s*Date|Bill\s*Date|Date\s*of\s*Issue|Date)\s*[:.-]?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})', # DD/MM/YYYY
            r'(?:Invoice\s*Date|Bill\s*Date|Date\s*of\s*Issue|Date)\s*[:.-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})', # Aug 01, 2026
            r'(?:Invoice\s*Date|Bill\s*Date|Date\s*of\s*Issue|Date)\s*[:.-]?\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})', # 01 August 2026
            r'\b(\d{4}-\d{2}-\d{2})\b',
            r'\b(\d{2}/\d{2}/\d{4})\b'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                return date_str
        return None

    def _extract_po_number(self, text: str):
        patterns = [
            r'(?:Purchase\s*Order\s*(?:No|Number|#)|PO\s*(?:No|Number|#)|P\.O\.\s*#?|Order\s*Ref|PO\s*Ref)\s*[:.-]?\s*([A-Za-z0-9-_/]+)',
            r'\b(PO[-_/][0-9A-Za-z-]+)\b'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                po = match.group(1).strip()
                if len(po) >= 3 and not po.lower() in ['date', 'number', 'box']:
                    return po
        return None

    def _extract_total_amount(self, text: str):
        # Detect currency
        currency = "INR"
        if "₹" in text or "INR" in text or "Rs." in text or "Rs " in text:
            currency = "INR"
        elif "$" in text or "USD" in text:
            currency = "USD"
        elif "€" in text or "EUR" in text:
            currency = "EUR"
        elif "£" in text or "GBP" in text:
            currency = "GBP"

        amount_patterns = [
            r'(?:Grand\s*Total|Total\s*Amount|Net\s*Payable|Amount\s*Due|Balance\s*Due|Invoice\s*Total|Total)\s*[:.-]?\s*(?:[₹$€£]|INR|USD|EUR|GBP|Rs\.?)?\s*([\d,]+\.?\d*)',
            r'(?:[₹$€£]|INR|USD|EUR|GBP|Rs\.?)\s*([\d,]+\.?\d*)\s*(?:Total|Grand Total)?'
        ]

        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for raw_val in reversed(matches):
                    cleaned_val = raw_val.replace(',', '').strip()
                    try:
                        val = float(cleaned_val)
                        if val > 0:
                            return val, currency
                    except ValueError:
                        continue
        return None, currency

def parse_invoice_text(text: str) -> dict:
    parser = InvoiceParser()
    return parser.parse(text)
