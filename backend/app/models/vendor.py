from datetime import datetime
import re
from app.extensions import db

class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    normalized_name = db.Column(db.String(150), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Invoices
    invoices = db.relationship('Invoice', backref='vendor', lazy=True)

    @staticmethod
    def normalize(name_str):
        if not name_str:
            return ""
        # Convert to lowercase and remove special characters/excess spaces
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', name_str.lower())
        return re.sub(r'\s+', ' ', cleaned).strip()

    def __init__(self, **kwargs):
        super(Vendor, self).__init__(**kwargs)
        if self.name and not self.normalized_name:
            self.normalized_name = self.normalize(self.name)

    def update_name(self, new_name):
        self.name = new_name
        self.normalized_name = self.normalize(new_name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'normalized_name': self.normalized_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'invoice_count': len(self.invoices),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
