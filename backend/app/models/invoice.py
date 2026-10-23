import json
from datetime import datetime
from app.extensions import db

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), nullable=True, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id', ondelete='SET NULL'), nullable=True)
    raw_vendor_name = db.Column(db.String(255), nullable=True)
    invoice_date = db.Column(db.String(50), nullable=True)
    total_amount = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=True, default='INR')
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    processing_status = db.Column(db.String(50), nullable=False, default='uploaded', index=True)
    # Statuses: uploaded, queued, processing, completed, failed
    error_message = db.Column(db.Text, nullable=True)
    extracted_text = db.Column(db.Text, nullable=True)
    extraction_confidence = db.Column(db.Float, default=0.0)

    # Verification Fields
    po_number = db.Column(db.String(100), nullable=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id', ondelete='SET NULL'), nullable=True)
    is_duplicate = db.Column(db.Boolean, default=False)
    duplicate_of_id = db.Column(db.Integer, nullable=True)
    vendor_match_status = db.Column(db.String(50), default='unmatched') # matched, ambiguous, unmatched
    vendor_match_score = db.Column(db.Float, default=0.0)
    po_match_status = db.Column(db.String(50), default='unlinked') # matched, mismatched, missing, unlinked
    po_amount_diff = db.Column(db.Float, default=0.0)

    # Explainable Risk Assessment
    risk_score = db.Column(db.Integer, default=0) # 0 - 100
    risk_level = db.Column(db.String(20), default='LOW') # LOW, MEDIUM, HIGH
    risk_factors = db.Column(db.Text, nullable=True) # JSON list of reasons

    # Optional AI Insight
    ai_summary = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_parsed_risk_factors(self):
        if not self.risk_factors:
            return []
        try:
            return json.loads(self.risk_factors)
        except Exception:
            return [self.risk_factors]

    def to_dict(self, include_text=False):
        # Determine best available vendor name (matched registered vendor, or raw extracted vendor name)
        display_vendor = self.vendor.name if self.vendor else self.raw_vendor_name

        data = {
            'id': self.id,
            'invoice_number': self.invoice_number or 'Pending Extraction',
            'vendor_id': self.vendor_id,
            'vendor_name': display_vendor,
            'raw_vendor_name': self.raw_vendor_name,
            'invoice_date': self.invoice_date,
            'total_amount': self.total_amount,
            'currency': self.currency or 'INR',
            'file_name': self.file_name,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
            'extraction_confidence': round(self.extraction_confidence or 0.0, 2),

            # Verification details
            'po_number': self.po_number,
            'purchase_order_id': self.purchase_order_id,
            'linked_po_number': self.purchase_order.po_number if self.purchase_order else None,
            'is_duplicate': bool(self.is_duplicate),
            'duplicate_of_id': self.duplicate_of_id,
            'vendor_match_status': self.vendor_match_status or 'unmatched',
            'vendor_match_score': round(self.vendor_match_score or 0.0, 2),
            'po_match_status': self.po_match_status or 'unlinked',
            'po_amount_diff': round(self.po_amount_diff or 0.0, 2),

            # Risk assessment
            'risk_score': self.risk_score or 0,
            'risk_level': self.risk_level or 'LOW',
            'risk_factors': self.get_parsed_risk_factors(),

            # AI summary
            'ai_summary': self.ai_summary,

            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_text:
            data['extracted_text'] = self.extracted_text or ""
        return data
