import io

def test_upload_invoice_success(client, auth_headers, dummy_pdf_bytes):
    data = {
        'file': (io.BytesIO(dummy_pdf_bytes), 'invoice_1024.pdf')
    }
    res = client.post('/api/invoices/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert res.status_code == 202
    res_data = res.get_json()
    assert res_data['message'] == 'Invoice uploaded successfully'
    assert 'invoice_id' in res_data
    assert res_data['status'] in ['queued', 'completed']

def test_upload_invalid_file_extension(client, auth_headers):
    data = {
        'file': (io.BytesIO(b"Plain text content"), 'notes.txt')
    }
    res = client.post('/api/invoices/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert res.status_code == 400
    assert 'Only PDF documents' in res.get_json()['error']

def test_upload_invalid_pdf_content(client, auth_headers):
    data = {
        'file': (io.BytesIO(b"Not a real pdf header"), 'fake.pdf')
    }
    res = client.post('/api/invoices/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert res.status_code == 400
    assert 'Invalid PDF file content' in res.get_json()['error']

def test_invoice_status_and_list(client, auth_headers, dummy_pdf_bytes):
    data = {
        'file': (io.BytesIO(dummy_pdf_bytes), 'sample.pdf')
    }
    res_up = client.post('/api/invoices/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    inv_id = res_up.get_json()['invoice_id']

    # Get status
    res_st = client.get(f'/api/invoices/{inv_id}/status', headers=auth_headers)
    assert res_st.status_code == 200
    assert 'status' in res_st.get_json()

    # List invoices
    res_list = client.get('/api/invoices', headers=auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.get_json()['invoices']) >= 1
