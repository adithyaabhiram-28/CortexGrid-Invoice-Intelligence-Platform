from app.services.invoice_parser import parse_invoice_text

def test_parse_invoice_text_sample_1():
    text = """
    TAX INVOICE
    Vendor: ABC Computers Pvt Ltd
    Invoice Number: INV-1024
    Date: 2026-08-01
    Grand Total: ₹45,000.00
    """
    result = parse_invoice_text(text)
    assert result['invoice_number'] == 'INV-1024'
    assert result['vendor_name'] == 'ABC Computers Pvt Ltd'
    assert result['invoice_date'] == '2026-08-01'
    assert result['total_amount'] == 45000.0
    assert result['currency'] == 'INR'

def test_parse_invoice_text_sample_2():
    text = """
    Bill Number: BILL-98765
    Supplier: TechCorp Solutions
    Bill Date: 15/09/2026
    Amount Due: $1,250.50
    """
    result = parse_invoice_text(text)
    assert result['invoice_number'] == 'BILL-98765'
    assert result['vendor_name'] == 'TechCorp Solutions'
    assert result['invoice_date'] == '15/09/2026'
    assert result['total_amount'] == 1250.50
    assert result['currency'] == 'USD'

def test_parse_empty_text():
    result = parse_invoice_text("")
    assert result['invoice_number'] is None
    assert result['total_amount'] is None
