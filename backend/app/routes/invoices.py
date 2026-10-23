import socket
import threading
from urllib.parse import urlparse
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.invoice import Invoice
from app.models.purchase_order import PurchaseOrder
from app.services.storage_service import LocalStorageService
from app.services.verification_service import VerificationService
from app.services.risk_service import RiskAssessmentService
from app.utils.validators import allowed_file
from app.middleware.auth_middleware import jwt_required

invoices_bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

def _is_redis_available(broker_url: str) -> bool:
    """Fast non-blocking socket check to see if Redis broker is reachable (timeout: 0.3s)."""
    try:
        parsed = urlparse(broker_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 6379
        with socket.create_connection((host, port), timeout=0.3):
            return True
    except Exception:
        return False

def _run_invoice_task_async(app, invoice_id: int):
    """Background worker thread runner with Flask application context."""
    with app.app_context():
        try:
            from app.tasks.invoice_tasks import process_invoice_logic
            process_invoice_logic(invoice_id)
        except Exception as e:
            app.logger.error(f"Background thread processing failed for invoice {invoice_id}: {e}")

@invoices_bp.route('/upload', methods=['POST'])
@jwt_required
def upload_invoice():
    if 'file' not in request.files and 'pdf' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file_obj = request.files.get('file') or request.files.get('pdf')
    if not file_obj or file_obj.filename == '':
        return jsonify({'error': 'Empty or missing file'}), 400

    if not allowed_file(file_obj.filename):
        return jsonify({'error': 'Only PDF documents are allowed'}), 400

    # Validate PDF Magic Bytes (%PDF-)
    header = file_obj.read(5)
    file_obj.seek(0)
    if header != b'%PDF-':
        return jsonify({'error': 'Invalid PDF file content'}), 400

    # Check file size limit
    file_obj.seek(0, 2)
    file_size = file_obj.tell()
    file_obj.seek(0)
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    if file_size > max_size:
        return jsonify({'error': f'File size exceeds limit of {max_size // (1024*1024)}MB'}), 413

    # Storage abstraction call
    storage = LocalStorageService(current_app.config['UPLOAD_FOLDER'])
    stored_relative_filename = storage.save_file(file_obj, file_obj.filename)

    # Create Database record with status = queued
    invoice = Invoice(
        file_name=file_obj.filename,
        file_path=stored_relative_filename,
        processing_status='queued'
    )
    db.session.add(invoice)
    db.session.commit()

    # Dispatch strategy:
    # 1. In testing mode: synchronous execution
    # 2. In normal mode: check Redis broker. If available, use Celery. Otherwise, launch background daemon thread.
    if current_app.config.get('TESTING'):
        from app.tasks.invoice_tasks import process_invoice_logic
        process_invoice_logic(invoice.id)
    else:
        broker_url = current_app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        redis_online = _is_redis_available(broker_url)

        if redis_online:
            try:
                from app.tasks.invoice_tasks import process_invoice_task
                process_invoice_task.apply_async(args=[invoice.id], retry=False)
            except Exception as e:
                current_app.logger.warning(f"Celery dispatch failed ({e}). Falling back to background thread.")
                t = threading.Thread(target=_run_invoice_task_async, args=(current_app._get_current_object(), invoice.id), daemon=True)
                t.start()
        else:
            current_app.logger.info("Redis broker offline. Using local background thread worker for async processing.")
            t = threading.Thread(target=_run_invoice_task_async, args=(current_app._get_current_object(), invoice.id), daemon=True)
            t.start()

    return jsonify({
        'message': 'Invoice uploaded successfully',
        'invoice_id': invoice.id,
        'status': invoice.processing_status
    }), 202

@invoices_bp.route('', methods=['GET'])
@jwt_required
def list_invoices():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    risk_level = request.args.get('risk_level', '').strip()
    vendor_id = request.args.get('vendor_id', type=int)

    query = Invoice.query
    if search:
        query = query.filter(
            (Invoice.invoice_number.ilike(f"%{search}%")) |
            (Invoice.raw_vendor_name.ilike(f"%{search}%")) |
            (Invoice.file_name.ilike(f"%{search}%"))
        )
    if status:
        query = query.filter(Invoice.processing_status == status)
    if risk_level:
        query = query.filter(Invoice.risk_level == risk_level.upper())
    if vendor_id:
        query = query.filter(Invoice.vendor_id == vendor_id)

    invoices = query.order_by(Invoice.created_at.desc()).all()

    # Calculate comprehensive summary stats
    all_invoices = Invoice.query.all()
    total = len(all_invoices)
    completed = sum(1 for inv in all_invoices if inv.processing_status == 'completed')
    processing = sum(1 for inv in all_invoices if inv.processing_status in ['queued', 'processing'])
    failed = sum(1 for inv in all_invoices if inv.processing_status == 'failed')
    low_risk = sum(1 for inv in all_invoices if inv.risk_level == 'LOW' and inv.processing_status == 'completed')
    medium_risk = sum(1 for inv in all_invoices if inv.risk_level == 'MEDIUM' and inv.processing_status == 'completed')
    high_risk = sum(1 for inv in all_invoices if inv.risk_level == 'HIGH' and inv.processing_status == 'completed')
    duplicates = sum(1 for inv in all_invoices if inv.is_duplicate)

    return jsonify({
        'invoices': [inv.to_dict(include_text=False) for inv in invoices],
        'stats': {
            'total': total,
            'completed': completed,
            'processing': processing,
            'failed': failed,
            'low_risk': low_risk,
            'medium_risk': medium_risk,
            'high_risk': high_risk,
            'duplicates': duplicates
        }
    }), 200

@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required
def get_invoice_details(invoice_id):
    invoice = db.session.get(Invoice, invoice_id) if hasattr(db.session, 'get') else Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    return jsonify({
        'invoice': invoice.to_dict(include_text=True)
    }), 200

@invoices_bp.route('/<int:invoice_id>/status', methods=['GET'])
@jwt_required
def get_invoice_status(invoice_id):
    invoice = db.session.get(Invoice, invoice_id) if hasattr(db.session, 'get') else Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    return jsonify({
        'invoice_id': invoice.id,
        'status': invoice.processing_status,
        'risk_level': invoice.risk_level,
        'risk_score': invoice.risk_score,
        'error_message': invoice.error_message
    }), 200

@invoices_bp.route('/<int:invoice_id>/link-po', methods=['POST'])
@jwt_required
def link_purchase_order(invoice_id):
    """Links or unlinks an invoice to a specific Purchase Order and triggers re-verification."""
    invoice = db.session.get(Invoice, invoice_id) if hasattr(db.session, 'get') else Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    data = request.get_json() or {}
    po_id = data.get('purchase_order_id')

    if po_id:
        po = db.session.get(PurchaseOrder, po_id) if hasattr(db.session, 'get') else PurchaseOrder.query.get(po_id)
        if not po:
            return jsonify({'error': 'Purchase Order not found'}), 404
        invoice.purchase_order_id = po.id
        invoice.po_number = po.po_number
        VerificationService.verify_purchase_order(invoice)
    else:
        # Unlink PO explicitly
        invoice.purchase_order_id = None
        invoice.po_number = None
        invoice.po_match_status = 'unlinked'
        invoice.po_amount_diff = 0.0

    RiskAssessmentService.evaluate(invoice)
    db.session.commit()

    return jsonify({
        'message': 'Purchase Order link updated successfully',
        'invoice': invoice.to_dict(include_text=True)
    }), 200

@invoices_bp.route('/<int:invoice_id>/reprocess', methods=['POST'])
@jwt_required
def reprocess_invoice(invoice_id):
    """Re-runs extraction, verification, and risk assessment for an invoice."""
    invoice = db.session.get(Invoice, invoice_id) if hasattr(db.session, 'get') else Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    from app.tasks.invoice_tasks import process_invoice_logic
    success = process_invoice_logic(invoice.id)
    
    # Reload invoice after update
    db.session.refresh(invoice)
    return jsonify({
        'message': 'Invoice reprocessed successfully' if success else 'Reprocessing completed with warnings',
        'invoice': invoice.to_dict(include_text=True)
    }), 200

@invoices_bp.route('/<int:invoice_id>', methods=['DELETE'])
@jwt_required
def delete_invoice(invoice_id):
    invoice = db.session.get(Invoice, invoice_id) if hasattr(db.session, 'get') else Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    storage = LocalStorageService(current_app.config['UPLOAD_FOLDER'])
    storage.delete_file(invoice.file_path)

    db.session.delete(invoice)
    db.session.commit()

    return jsonify({'message': 'Invoice deleted successfully'}), 200
