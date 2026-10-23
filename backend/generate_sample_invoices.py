"""
CortexGrid Sample Invoice PDF Generator
Generates realistic test invoice PDFs for major project demonstration and review testing:
1. Clean Verified Invoice (matches registered vendor & PO -> Low Risk)
2. Price Mismatch Invoice (invoice total exceeds PO total -> Medium/High Risk)
3. Unrecognized Vendor Invoice (unregistered supplier, no PO -> High Risk)
4. Duplicate Invoice (same invoice number as sample 1 -> Duplicate Flag)
"""

import os
try:
    import pymupdf as fitz
except ImportError:
    import fitz

def create_invoice_pdf(output_path: str, invoice_no: str, vendor_name: str, date_str: str,
                       total_str: str, po_str: str = "", items = None):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4 size

    # Draw header banner
    rect = fitz.Rect(40, 40, 555, 110)
    page.draw_rect(rect, color=(0.01, 0.52, 0.78), fill=(0.05, 0.1, 0.18), width=1.5)

    # Header text
    page.insert_text((55, 75), "TAX INVOICE / BILL OF SUPPLY", fontsize=16, fontname="helv", color=(1, 1, 1))
    page.insert_text((55, 95), "Commercial Accounts Payable Document", fontsize=10, fontname="helv", color=(0.4, 0.7, 0.9))

    # Vendor Block
    page.insert_text((55, 140), "VENDOR / SUPPLIER DETAILS:", fontsize=11, fontname="helv", color=(0.2, 0.2, 0.2))
    page.insert_text((55, 160), f"Vendor Name: {vendor_name}", fontsize=12, fontname="helv", color=(0, 0, 0))
    page.insert_text((55, 178), "GSTIN / Tax ID: 29AABCU9603R1ZM", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))
    page.insert_text((55, 194), "Address: Cyber City, Tower B, Level 4, Tech Zone, Bangalore - 560100", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))

    # Invoice Metadata Box
    meta_rect = fitz.Rect(340, 130, 555, 230)
    page.draw_rect(meta_rect, color=(0.8, 0.8, 0.8), fill=(0.96, 0.97, 0.98), width=1)
    page.insert_text((355, 155), f"Invoice Number: {invoice_no}", fontsize=11, fontname="helv", color=(0.01, 0.4, 0.7))
    page.insert_text((355, 175), f"Invoice Date: {date_str}", fontsize=10, fontname="helv", color=(0.2, 0.2, 0.2))
    if po_str:
        page.insert_text((355, 195), f"Purchase Order: {po_str}", fontsize=10, fontname="helv", color=(0.1, 0.5, 0.3))
    page.insert_text((355, 215), "Payment Terms: Net 30 Days", fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))

    # Table Header
    page.draw_rect(fitz.Rect(40, 260, 555, 285), fill=(0.1, 0.15, 0.22))
    page.insert_text((55, 277), "Item Description", fontsize=10, fontname="helv", color=(1, 1, 1))
    page.insert_text((350, 277), "Qty", fontsize=10, fontname="helv", color=(1, 1, 1))
    page.insert_text((420, 277), "Unit Price", fontsize=10, fontname="helv", color=(1, 1, 1))
    page.insert_text((490, 277), "Total", fontsize=10, fontname="helv", color=(1, 1, 1))

    # Items
    y = 310
    if not items:
        items = [
            ("Enterprise Cloud Server Subscription", "1", "45,000.00", "45,000.00"),
            ("Dedicated Support SLA (Monthly)", "1", "5,000.00", "5,000.00")
        ]

    for desc, qty, price, row_total in items:
        page.insert_text((55, y), desc, fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
        page.insert_text((355, y), qty, fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
        page.insert_text((420, y), price, fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
        page.insert_text((490, y), row_total, fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
        page.draw_line(fitz.Point(40, y + 10), fitz.Point(555, y + 10), color=(0.88, 0.88, 0.88), width=0.5)
        y += 30

    # Total Box
    tot_rect = fitz.Rect(340, y + 20, 555, y + 75)
    page.draw_rect(tot_rect, color=(0.01, 0.52, 0.78), fill=(0.94, 0.98, 1.0), width=1.5)
    page.insert_text((355, y + 45), "Grand Total Amount:", fontsize=10, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text((355, y + 65), f"Total: {total_str}", fontsize=14, fontname="helv", color=(0.01, 0.52, 0.78))

    # Footer
    page.insert_text((55, 780), "This is a computer-generated tax invoice. Verified by CortexGrid Intelligence Platform.", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()
    print(f"Generated sample invoice: {output_path}")

if __name__ == '__main__':
    base_dir = os.path.join(os.path.dirname(__file__), 'sample_invoices')
    os.makedirs(base_dir, exist_ok=True)

    # 1. Clean Verified Invoice
    create_invoice_pdf(
        os.path.join(base_dir, '1_Verified_Invoice_PO_Match.pdf'),
        invoice_no="INV-2026-001",
        vendor_name="ABC Computers Pvt Ltd",
        date_str="2026-08-10",
        total_str="INR 50,000.00",
        po_str="PO-2026-7890",
        items=[
            ("Dell UltraSharp 27 Monitor", "2", "25,000.00", "50,000.00")
        ]
    )

    # 2. Price Mismatch Invoice
    create_invoice_pdf(
        os.path.join(base_dir, '2_Price_Mismatch_PO_Overbilling.pdf'),
        invoice_no="INV-2026-002",
        vendor_name="ABC Computers Pvt Ltd",
        date_str="2026-08-12",
        total_str="INR 75,000.00",
        po_str="PO-2026-7890",
        items=[
            ("Dell UltraSharp 27 Monitor", "2", "25,000.00", "50,000.00"),
            ("Unapproved Expedited Shipping Surcharge", "1", "25,000.00", "25,000.00")
        ]
    )

    # 3. Unrecognized Vendor & No PO (High Risk)
    create_invoice_pdf(
        os.path.join(base_dir, '3_Unregistered_Vendor_No_PO.pdf'),
        invoice_no="INV-UNKNOWN-99",
        vendor_name="Phantom Technologies Global LLC",
        date_str="2026-08-14",
        total_str="INR 125,000.00",
        po_str="",
        items=[
            ("Advisory Consulting Services", "1", "125,000.00", "125,000.00")
        ]
    )

    # 4. Duplicate Invoice
    create_invoice_pdf(
        os.path.join(base_dir, '4_Duplicate_Invoice_Submission.pdf'),
        invoice_no="INV-2026-001",
        vendor_name="ABC Computers Pvt Ltd",
        date_str="2026-08-10",
        total_str="INR 50,000.00",
        po_str="PO-2026-7890"
    )
