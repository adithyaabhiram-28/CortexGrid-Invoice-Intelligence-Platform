def test_create_and_list_vendors(client, auth_headers):
    # Create Vendor
    res = client.post('/api/vendors', json={
        'name': 'ABC Computers Pvt Ltd',
        'email': 'billing@abccomputers.com',
        'phone': '+91 9876543210',
        'address': 'Tech Park, Bangalore'
    }, headers=auth_headers)
    assert res.status_code == 201
    vendor_id = res.get_json()['vendor']['id']

    # List Vendors
    res_list = client.get('/api/vendors', headers=auth_headers)
    assert res_list.status_code == 200
    vendors = res_list.get_json()['vendors']
    assert len(vendors) == 1
    assert vendors[0]['name'] == 'ABC Computers Pvt Ltd'

    # Get Single Vendor
    res_single = client.get(f'/api/vendors/{vendor_id}', headers=auth_headers)
    assert res_single.status_code == 200
    assert res_single.get_json()['vendor']['id'] == vendor_id

def test_update_and_delete_vendor(client, auth_headers):
    res = client.post('/api/vendors', json={'name': 'XYZ Suppliers'}, headers=auth_headers)
    vendor_id = res.get_json()['vendor']['id']

    # Update
    res_upd = client.put(f'/api/vendors/{vendor_id}', json={'name': 'XYZ Global Suppliers'}, headers=auth_headers)
    assert res_upd.status_code == 200
    assert res_upd.get_json()['vendor']['name'] == 'XYZ Global Suppliers'

    # Delete
    res_del = client.delete(f'/api/vendors/{vendor_id}', headers=auth_headers)
    assert res_del.status_code == 200

    # Verify 404
    res_404 = client.get(f'/api/vendors/{vendor_id}', headers=auth_headers)
    assert res_404.status_code == 404
