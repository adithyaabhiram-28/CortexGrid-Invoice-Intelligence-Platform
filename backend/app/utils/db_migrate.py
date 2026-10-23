import logging
from sqlalchemy import text
from app.extensions import db

logger = logging.getLogger(__name__)

def ensure_schema_updates(app):
    """
    Safely checks and adds any missing columns to existing tables in development.
    Preserves all existing user records, vendor records, and uploaded invoices.
    """
    with app.app_context():
        engine = db.engine
        inspector = db.inspect(engine)
        existing_tables = inspector.get_table_names()

        # Columns to ensure on 'invoices' table
        invoice_columns = {col['name'] for col in inspector.get_columns('invoices')} if 'invoices' in existing_tables else set()

        columns_to_add = [
            ('raw_vendor_name', 'VARCHAR(255)'),
            ('po_number', 'VARCHAR(100)'),
            ('purchase_order_id', 'INTEGER'),
            ('is_duplicate', 'BOOLEAN DEFAULT 0'),
            ('duplicate_of_id', 'INTEGER'),
            ('vendor_match_status', 'VARCHAR(50) DEFAULT "unmatched"'),
            ('vendor_match_score', 'FLOAT DEFAULT 0.0'),
            ('po_match_status', 'VARCHAR(50) DEFAULT "unlinked"'),
            ('po_amount_diff', 'FLOAT DEFAULT 0.0'),
            ('risk_score', 'INTEGER DEFAULT 0'),
            ('risk_level', 'VARCHAR(20) DEFAULT "LOW"'),
            ('risk_factors', 'TEXT'),
            ('ai_summary', 'TEXT'),
            ('extraction_confidence', 'FLOAT DEFAULT 0.0')
        ]

        with engine.connect() as conn:
            for col_name, col_type in columns_to_add:
                if col_name not in invoice_columns:
                    try:
                        conn.execute(text(f"ALTER TABLE invoices ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        logger.info(f"Added column {col_name} to invoices table.")
                    except Exception as e:
                        logger.warning(f"Could not add column {col_name} to invoices (might already exist): {e}")

        logger.info("Schema migration check completed successfully.")
