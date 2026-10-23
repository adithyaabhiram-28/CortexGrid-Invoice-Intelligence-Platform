def test_register_success(client):
    res = client.post('/api/auth/register', json={
        'name': 'Adithya Abhiram',
        'email': 'adithya@cortexgrid.com',
        'password': 'securepassword123',
        'role': 'admin'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert 'token' in data
    assert data['user']['email'] == 'adithya@cortexgrid.com'
    assert data['user']['role'] == 'admin'

def test_register_duplicate_email(client):
    client.post('/api/auth/register', json={
        'name': 'User One',
        'email': 'duplicate@cortexgrid.com',
        'password': 'password123'
    })
    res = client.post('/api/auth/register', json={
        'name': 'User Two',
        'email': 'duplicate@cortexgrid.com',
        'password': 'password123'
    })
    assert res.status_code == 409

def test_login_success(client):
    client.post('/api/auth/register', json={
        'name': 'Login User',
        'email': 'login@cortexgrid.com',
        'password': 'mypassword123'
    })
    res = client.post('/api/auth/login', json={
        'email': 'login@cortexgrid.com',
        'password': 'mypassword123'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'token' in data

def test_login_invalid_password(client):
    client.post('/api/auth/register', json={
        'name': 'Login User',
        'email': 'login2@cortexgrid.com',
        'password': 'mypassword123'
    })
    res = client.post('/api/auth/login', json={
        'email': 'login2@cortexgrid.com',
        'password': 'wrongpassword'
    })
    assert res.status_code == 401

def test_get_me(client, auth_headers):
    res = client.get('/api/auth/me', headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()['user']['email'] == 'testuser@cortexgrid.com'

def test_protected_endpoint_unauthorized(client):
    res = client.get('/api/auth/me')
    assert res.status_code == 401
