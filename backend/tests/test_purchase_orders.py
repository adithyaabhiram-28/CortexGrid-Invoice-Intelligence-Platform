import pytest

def test_create_and_list_purchase_orders(client, auth_headers):
    # 1. Create a Vendor
    v_res = client.post('/api/vendors', json={
        'name': 'Apex Hardware Solutions Pvt Ltd',
        'email': 'sales@apexhardware.com'
    }, headers=auth_headers)
    vendor_id = v_res.get_json()['vendor']['id']

    # 2. Create Purchase Order with Items
    po_res = client.post('/api/purchase-orders', json={
        'po_number': 'PO-2026-7890',
        'vendor_id': vendor_id,
        'po_date': '2026-08-15',
        'currency': 'INR',
        'description': 'Office IT Hardware Procurement',
        'items': [
            {'item_description': 'Dell UltraSharp 27" Monitor', 'quantity': 2, 'unit_price': 25000.0, 'total_amount': 50000.0},
            {'item_description': 'Mechanical Keyboard', 'quantity': 2, 'unit_price': 5000.0, 'total_amount': 10000.0}
        ]
    }, headers=auth_headers)

    assert po_res.status_code == 201
    po_data = po_res.get_json()['purchase_order']
    assert po_data['po_number'] == 'PO-2026-7890'
    assert po_data['total_amount'] == 60000.0
    assert po_data['vendor_name'] == 'Apex Hardware Solutions Pvt Ltd'
    assert len(po_data['items']) == 2
    po_id = po_data['id']

    # 3. List Purchase Orders
    list_res = client.get('/api/purchase-orders', headers=auth_headers)
    assert list_res.status_code == 200
    orders = list_res.get_json()['purchase_orders']
    assert any(o['po_number'] == 'PO-2026-7890' for o in orders)

    # 4. Get Single Purchase Order
    single_res = client.get(f'/api/purchase-orders/{po_id}', headers=auth_headers)
    assert single_res.status_code == 200
    assert single_res.get_json()['purchase_order']['id'] == po_id

    # 5. Duplicate PO Number Rejection
    dup_res = client.post('/api/purchase-orders', json={
        'po_number': 'PO-2026-7890',
        'vendor_id': vendor_id,
        'total_amount': 1000.0
    }, headers=auth_headers)
    assert dup_res.status_code == 409

def test_update_and_delete_purchase_order(client, auth_headers):
    po_res = client.post('/api/purchase-orders', json={
        'po_number': 'PO-TEMP-001',
        'total_amount': 5000.0,
        'currency': 'INR'
    }, headers=auth_headers)
    po_id = po_res.get_json()['purchase_order']['id']

    # Update PO
    upd_res = client.put(f'/api/purchase-orders/{po_id}', json={
        'total_amount': 7500.0,
        'status': 'fulfilled'
    }, headers=auth_headers)
    assert upd_res.status_code == 200
    assert upd_res.get_json()['purchase_order']['total_amount'] == 7500.0
    assert upd_res.get_json()['purchase_order']['status'] == 'fulfilled'

    # Delete PO
    del_res = client.delete(f'/api/purchase-orders/{po_id}', headers=auth_headers)
    assert del_res.status_code == 200

    # Verify 404
    get_res = client.get(f'/api/purchase-orders/{po_id}', headers=auth_headers)
    assert get_res.status_code == 404
