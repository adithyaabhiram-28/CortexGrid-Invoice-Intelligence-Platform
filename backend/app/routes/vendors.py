from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.vendor import Vendor
from app.middleware.auth_middleware import jwt_required

vendors_bp = Blueprint('vendors', __name__, url_prefix='/api/vendors')

@vendors_bp.route('', methods=['GET'])
@jwt_required
def list_vendors():
    search = request.args.get('search', '').strip()
    query = Vendor.query
    if search:
        norm_search = Vendor.normalize(search)
        query = query.filter(Vendor.normalized_name.contains(norm_search))
    
    vendors = query.order_by(Vendor.created_at.desc()).all()
    return jsonify({
        'vendors': [v.to_dict() for v in vendors]
    }), 200

@vendors_bp.route('/<int:vendor_id>', methods=['GET'])
@jwt_required
def get_vendor(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404
    return jsonify({'vendor': vendor.to_dict()}), 200

@vendors_bp.route('', methods=['POST'])
@jwt_required
def create_vendor():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()

    if not name:
        return jsonify({'error': 'Vendor name is required'}), 400

    norm_name = Vendor.normalize(name)
    existing = Vendor.query.filter_by(normalized_name=norm_name).first()
    if existing:
        return jsonify({'error': 'Vendor with similar name already exists'}), 409

    vendor = Vendor(
        name=name,
        normalized_name=norm_name,
        email=email or None,
        phone=phone or None,
        address=address or None
    )
    db.session.add(vendor)
    db.session.commit()

    return jsonify({
        'message': 'Vendor created successfully',
        'vendor': vendor.to_dict()
    }), 201

@vendors_bp.route('/<int:vendor_id>', methods=['PUT'])
@jwt_required
def update_vendor(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404

    data = request.get_json() or {}
    name = data.get('name', '').strip() if 'name' in data else vendor.name
    email = data.get('email', '').strip() if 'email' in data else vendor.email
    phone = data.get('phone', '').strip() if 'phone' in data else vendor.phone
    address = data.get('address', '').strip() if 'address' in data else vendor.address

    if not name:
        return jsonify({'error': 'Vendor name cannot be empty'}), 400

    vendor.update_name(name)
    vendor.email = email or None
    vendor.phone = phone or None
    vendor.address = address or None

    db.session.commit()

    return jsonify({
        'message': 'Vendor updated successfully',
        'vendor': vendor.to_dict()
    }), 200

@vendors_bp.route('/<int:vendor_id>', methods=['DELETE'])
@jwt_required
def delete_vendor(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404

    db.session.delete(vendor)
    db.session.commit()

    return jsonify({'message': 'Vendor deleted successfully'}), 200
