import pytest
import os
import io
from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Creates a default user and returns Authorization headers with JWT token."""
    response = client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'testuser@cortexgrid.com',
        'password': 'password123',
        'role': 'finance_user'
    })
    token = response.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def dummy_pdf_bytes():
    """Generates a minimal valid PDF byte string for file upload testing."""
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kinds [] /Count 1 /Kids [3 0 R] >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        b"4 0 obj << /Length 55 >> stream\n"
        b"BT /F1 12 Tf 100 700 Td (Invoice No: INV-9999 Total: 1500) Tj ET\n"
        b"endstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f\n"
        b"trailer << /Size 5 /Root 1 0 R >>\nstartxref\n300\n%%EOF"
    )
    return pdf_content
