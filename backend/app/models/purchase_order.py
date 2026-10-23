from datetime import datetime
from app.extensions import db

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id', ondelete='SET NULL'), nullable=True)
    po_date = db.Column(db.String(50), nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(10), nullable=False, default='INR')
    status = db.Column(db.String(50), nullable=False, default='open')  # open, matched, fulfilled, cancelled
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vendor = db.relationship('Vendor', backref='purchase_orders', lazy=True)
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan', lazy=True)
    invoices = db.relationship('Invoice', backref='purchase_order', lazy=True)

    def to_dict(self, include_items=True):
        data = {
            'id': self.id,
            'po_number': self.po_number,
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor.name if self.vendor else None,
            'po_date': self.po_date,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'status': self.status,
            'description': self.description,
            'items_count': len(self.items),
            'linked_invoices_count': len(self.invoices),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data


class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'

    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id', ondelete='CASCADE'), nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'po_id': self.po_id,
            'item_description': self.item_description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_amount': self.total_amount
        }
