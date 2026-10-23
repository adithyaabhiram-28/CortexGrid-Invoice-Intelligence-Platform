from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.middleware.auth_middleware import jwt_required
from app.services.verification_service import VerificationService
from app.services.risk_service import RiskAssessmentService

purchase_orders_bp = Blueprint('purchase_orders', __name__, url_prefix='/api/purchase-orders')

@purchase_orders_bp.route('', methods=['GET'])
@jwt_required
def list_purchase_orders():
    search = request.args.get('search', '').strip()
    vendor_id = request.args.get('vendor_id', type=int)
    status = request.args.get('status', '').strip()

    query = PurchaseOrder.query

    if search:
        query = query.filter(
            (PurchaseOrder.po_number.ilike(f"%{search}%")) |
            (PurchaseOrder.description.ilike(f"%{search}%"))
        )
    if vendor_id:
        query = query.filter(PurchaseOrder.vendor_id == vendor_id)
    if status:
        query = query.filter(PurchaseOrder.status == status)

    orders = query.order_by(PurchaseOrder.created_at.desc()).all()
    return jsonify({
        'purchase_orders': [po.to_dict(include_items=False) for po in orders],
        'count': len(orders)
    }), 200

@purchase_orders_bp.route('/<int:po_id>', methods=['GET'])
@jwt_required
def get_purchase_order(po_id):
    po = db.session.get(PurchaseOrder, po_id) if hasattr(db.session, 'get') else PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify({'error': 'Purchase Order not found'}), 404

    data = po.to_dict(include_items=True)
    # Include list of linked invoices
    data['linked_invoices'] = [inv.to_dict() for inv in po.invoices]
    return jsonify({'purchase_order': data}), 200

@purchase_orders_bp.route('', methods=['POST'])
@jwt_required
def create_purchase_order():
    data = request.get_json() or {}
    po_number = data.get('po_number', '').strip().upper()
    vendor_id = data.get('vendor_id')
    po_date = data.get('po_date', '').strip()
    total_amount = data.get('total_amount')
    currency = data.get('currency', 'INR').strip().upper()
    description = data.get('description', '').strip()
    items_data = data.get('items', [])

    if not po_number:
        return jsonify({'error': 'Purchase Order Number (PO Number) is required'}), 400

    existing = PurchaseOrder.query.filter_by(po_number=po_number).first()
    if existing:
        return jsonify({'error': f"Purchase Order with number '{po_number}' already exists."}), 409

    if vendor_id:
        vendor = db.session.get(Vendor, vendor_id) if hasattr(db.session, 'get') else Vendor.query.get(vendor_id)
        if not vendor:
            return jsonify({'error': 'Specified vendor does not exist'}), 400

    # Auto-calculate total from items if items provided and total not explicitly passed
    calc_total = 0.0
    items_to_add = []
    for itm in items_data:
        desc = itm.get('item_description', '').strip()
        qty = float(itm.get('quantity', 1.0))
        price = float(itm.get('unit_price', 0.0))
        item_total = float(itm.get('total_amount', round(qty * price, 2)))
        calc_total += item_total
        items_to_add.append(PurchaseOrderItem(
            item_description=desc or 'Item',
            quantity=qty,
            unit_price=price,
            total_amount=item_total
        ))

    final_total = float(total_amount) if total_amount is not None else calc_total

    po = PurchaseOrder(
        po_number=po_number,
        vendor_id=vendor_id,
        po_date=po_date or None,
        total_amount=final_total,
        currency=currency or 'INR',
        description=description or None,
        status='open'
    )
    po.items = items_to_add

    db.session.add(po)
    db.session.commit()

    return jsonify({
        'message': 'Purchase Order created successfully',
        'purchase_order': po.to_dict(include_items=True)
    }), 201

@purchase_orders_bp.route('/<int:po_id>', methods=['PUT'])
@jwt_required
def update_purchase_order(po_id):
    po = db.session.get(PurchaseOrder, po_id) if hasattr(db.session, 'get') else PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify({'error': 'Purchase Order not found'}), 404

    data = request.get_json() or {}
    if 'po_number' in data and data['po_number'].strip():
        po.po_number = data['po_number'].strip().upper()
    if 'vendor_id' in data:
        po.vendor_id = data['vendor_id']
    if 'po_date' in data:
        po.po_date = data['po_date'].strip()
    if 'total_amount' in data and data['total_amount'] is not None:
        po.total_amount = float(data['total_amount'])
    if 'currency' in data and data['currency']:
        po.currency = data['currency'].strip().upper()
    if 'status' in data and data['status']:
        po.status = data['status']
    if 'description' in data:
        po.description = data['description'].strip()

    db.session.commit()

    return jsonify({
        'message': 'Purchase Order updated successfully',
        'purchase_order': po.to_dict(include_items=True)
    }), 200

@purchase_orders_bp.route('/<int:po_id>', methods=['DELETE'])
@jwt_required
def delete_purchase_order(po_id):
    po = db.session.get(PurchaseOrder, po_id) if hasattr(db.session, 'get') else PurchaseOrder.query.get(po_id)
    if not po:
        return jsonify({'error': 'Purchase Order not found'}), 404

    db.session.delete(po)
    db.session.commit()
    return jsonify({'message': 'Purchase Order deleted successfully'}), 200
