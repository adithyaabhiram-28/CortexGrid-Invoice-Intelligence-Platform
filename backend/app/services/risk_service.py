import json
import logging
from app.models.invoice import Invoice

logger = logging.getLogger(__name__)

class RiskAssessmentService:
    """
    Explainable Rule-Based Risk Assessment Engine.
    Evaluates verification results and extraction completeness to compute a transparent risk score (0-100),
    a risk category (LOW, MEDIUM, HIGH), and a documented breakdown of reasons.
    """

    @staticmethod
    def evaluate(invoice: Invoice) -> dict:
        score = 0
        factors = []

        # Rule 1: Duplicate Invoice Check (Weight: 45 points)
        if invoice.is_duplicate:
            score += 45
            factors.append({
                "rule": "DUPLICATE_INVOICE",
                "severity": "HIGH",
                "points": 45,
                "description": f"Duplicate invoice detected in repository (matches Invoice #{invoice.duplicate_of_id}). Potential double billing."
            })

        # Rule 2: Purchase Order Comparison (Weight: 15-30 points)
        if invoice.po_match_status == 'mismatched':
            diff = abs(invoice.po_amount_diff or 0.0)
            # Evaluate percentage difference if PO available
            pct = 10.0
            if invoice.purchase_order and invoice.purchase_order.total_amount > 0:
                pct = (diff / invoice.purchase_order.total_amount) * 100

            if pct > 5.0:
                score += 30
                factors.append({
                    "rule": "PO_AMOUNT_MISMATCH_MAJOR",
                    "severity": "HIGH",
                    "points": 30,
                    "description": f"Invoice total exceeds Purchase Order by {invoice.currency} {diff:,.2f} ({pct:.1f}% variance > 5% threshold)."
                })
            else:
                score += 15
                factors.append({
                    "rule": "PO_AMOUNT_MISMATCH_MINOR",
                    "severity": "MEDIUM",
                    "points": 15,
                    "description": f"Minor price variance with Purchase Order of {invoice.currency} {diff:,.2f} ({pct:.1f}% variance)."
                })

        elif invoice.po_match_status == 'missing':
            # Missing PO: higher risk for large invoices
            inv_total = invoice.total_amount or 0.0
            if inv_total >= 10000:
                score += 20
                factors.append({
                    "rule": "PO_MISSING_HIGH_VALUE",
                    "severity": "MEDIUM",
                    "points": 20,
                    "description": f"No Purchase Order linked for high-value invoice ({invoice.currency} {inv_total:,.2f}). Requires approval."
                })
            else:
                score += 10
                factors.append({
                    "rule": "PO_MISSING",
                    "severity": "LOW",
                    "points": 10,
                    "description": "Invoice does not cite or match a registered Purchase Order."
                })

        # Rule 3: Vendor Verification (Weight: 10-20 points)
        if invoice.vendor_match_status == 'unmatched':
            score += 20
            vendor_display = invoice.raw_vendor_name or "Unknown Entity"
            factors.append({
                "rule": "UNRECOGNIZED_VENDOR",
                "severity": "MEDIUM",
                "points": 20,
                "description": f"Vendor '{vendor_display}' is not in the approved vendor registry."
            })
        elif invoice.vendor_match_status == 'ambiguous':
            score += 10
            factors.append({
                "rule": "AMBIGUOUS_VENDOR_MATCH",
                "severity": "LOW",
                "points": 10,
                "description": f"Extracted vendor name '{invoice.raw_vendor_name}' could not be matched with high confidence."
            })

        # Rule 4: Critical Field Completeness (Weight: 10-20 points each)
        if not invoice.invoice_number or invoice.invoice_number == 'Pending Extraction':
            score += 15
            factors.append({
                "rule": "MISSING_INVOICE_NUMBER",
                "severity": "MEDIUM",
                "points": 15,
                "description": "Invoice number could not be detected from document text."
            })

        if not invoice.invoice_date:
            score += 10
            factors.append({
                "rule": "MISSING_INVOICE_DATE",
                "severity": "LOW",
                "points": 10,
                "description": "Invoice date was not found in document text."
            })

        if invoice.total_amount is None:
            score += 20
            factors.append({
                "rule": "MISSING_TOTAL_AMOUNT",
                "severity": "HIGH",
                "points": 20,
                "description": "Financial total could not be determined from invoice text."
            })

        # Cap score between 0 and 100
        final_score = min(max(score, 0), 100)

        # Categorize
        if final_score <= 25:
            risk_level = "LOW"
        elif final_score <= 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Update invoice model attributes
        invoice.risk_score = final_score
        invoice.risk_level = risk_level
        invoice.risk_factors = json.dumps(factors)

        logger.info(f"Risk Assessment for Invoice #{invoice.id}: Score={final_score}, Level={risk_level}, Factors={len(factors)}")

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "factors": factors
        }
