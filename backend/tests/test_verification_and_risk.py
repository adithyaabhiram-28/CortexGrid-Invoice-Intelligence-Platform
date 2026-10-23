import io
import pytest
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.services.verification_service import VerificationService
from app.services.risk_service import RiskAssessmentService

def make_test_pdf(text_content: str) -> bytes:
    """Helper to generate a minimal PDF stream with custom text content."""
    stream_content = f"BT /F1 12 Tf 100 700 Td ({text_content}) Tj ET".encode('latin-1')
    length = len(stream_content)
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kinds [] /Count 1 /Kids [3 0 R] >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        b"4 0 obj << /Length " + str(length).encode('ascii') + b" >> stream\n" +
        stream_content + b"\nendstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f\n"
        b"trailer << /Size 5 /Root 1 0 R >>\nstartxref\n300\n%%EOF"
    )
    return pdf

def test_duplicate_invoice_detection(client, auth_headers):
    pdf_bytes = make_test_pdf("Invoice No: INV-DUP-100 Vendor: Acme Corp Total: 5000 Date: 2026-08-01")

    # Upload first invoice
    res1 = client.post('/api/invoices/upload', data={'file': (io.BytesIO(pdf_bytes), 'first.pdf')},
                       content_type='multipart/form-data', headers=auth_headers)
    assert res1.status_code == 202
    inv1_id = res1.get_json()['invoice_id']

    # Upload second invoice with duplicate invoice number
    res2 = client.post('/api/invoices/upload', data={'file': (io.BytesIO(pdf_bytes), 'second.pdf')},
                       content_type='multipart/form-data', headers=auth_headers)
    assert res2.status_code == 202
    inv2_id = res2.get_json()['invoice_id']

    # Inspect second invoice details
    detail2 = client.get(f'/api/invoices/{inv2_id}', headers=auth_headers).get_json()['invoice']
    assert detail2['is_duplicate'] is True
    assert detail2['duplicate_of_id'] == inv1_id
    assert detail2['risk_level'] in ['MEDIUM', 'HIGH']
    assert any(f['rule'] == 'DUPLICATE_INVOICE' for f in detail2['risk_factors'])

def test_po_amount_verification_and_link(client, auth_headers):
    # 1. Create a Purchase Order for 50,000
    po_res = client.post('/api/purchase-orders', json={
        'po_number': 'PO-MATCH-2026',
        'total_amount': 50000.0,
        'currency': 'INR'
    }, headers=auth_headers)
    po_id = po_res.get_json()['purchase_order']['id']

    # 2. Upload Invoice with PO # cited and mismatched total (55,000)
    pdf_mismatch = make_test_pdf("Invoice No: INV-PO-888 Total: 55000 PO No: PO-MATCH-2026 Date: 2026-09-01")
    up_res = client.post('/api/invoices/upload', data={'file': (io.BytesIO(pdf_mismatch), 'po_inv.pdf')},
                         content_type='multipart/form-data', headers=auth_headers)
    inv_id = up_res.get_json()['invoice_id']

    detail = client.get(f'/api/invoices/{inv_id}', headers=auth_headers).get_json()['invoice']
    assert detail['purchase_order_id'] == po_id
    assert detail['po_match_status'] == 'mismatched'
    assert detail['po_amount_diff'] == 5000.0
    assert any('PO_AMOUNT_MISMATCH' in f['rule'] for f in detail['risk_factors'])

    # 3. Test explicit manual PO link endpoint
    link_res = client.post(f'/api/invoices/{inv_id}/link-po', json={'purchase_order_id': None}, headers=auth_headers)
    assert link_res.status_code == 200
    updated_detail = link_res.get_json()['invoice']
    assert updated_detail['purchase_order_id'] is None
    assert updated_detail['po_match_status'] == 'unlinked'

def test_invoice_reprocess_endpoint(client, auth_headers):
    pdf_bytes = make_test_pdf("Invoice No: INV-REPROC-1 Total: 12000 Date: 2026-09-15")
    up_res = client.post('/api/invoices/upload', data={'file': (io.BytesIO(pdf_bytes), 'reproc.pdf')},
                         content_type='multipart/form-data', headers=auth_headers)
    inv_id = up_res.get_json()['invoice_id']

    reproc_res = client.post(f'/api/invoices/{inv_id}/reprocess', headers=auth_headers)
    assert reproc_res.status_code == 200
    data = reproc_res.get_json()['invoice']
    assert data['invoice_number'] == 'INV-REPROC-1'
    assert data['total_amount'] == 12000.0
    assert 'risk_level' in data
