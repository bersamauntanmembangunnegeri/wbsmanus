from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.layout import WebsiteLayout, SiteSettings
from src.models.product import Product, Category
from src.models.order import Order
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Helper function to check admin access"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return False, jsonify({'error': 'Admin access required'}), 403
    return True, user, None

# Dashboard statistics
@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        # Get various statistics
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()
        
        # Recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        
        # Order status counts
        order_status_counts = db.session.query(
            Order.status, 
            func.count(Order.id)
        ).group_by(Order.status).all()
        
        # Revenue calculation (sum of total_price)
        total_revenue = db.session.query(func.sum(Order.total_price)).scalar() or 0
        
        return jsonify({
            'total_products': total_products,
            'total_orders': total_orders,
            'total_users': total_users,
            'total_categories': total_categories,
            'total_revenue': float(total_revenue),
            'recent_orders': [order.to_dict() for order in recent_orders],
            'order_status_counts': dict(order_status_counts)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Website Layout Management
@admin_bp.route('/layout', methods=['GET'])
@jwt_required()
def get_layout_sections():
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        sections = WebsiteLayout.query.order_by(WebsiteLayout.sort_order).all()
        return jsonify([section.to_dict() for section in sections])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/layout', methods=['POST'])
@jwt_required()
def create_layout_section():
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        data = request.json
        section = WebsiteLayout(
            section_name=data['section_name'],
            section_type=data['section_type'],
            content=data.get('content', {}),
            settings=data.get('settings', {}),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(section)
        db.session.commit()
        return jsonify(section.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/layout/<int:section_id>', methods=['PUT'])
@jwt_required()
def update_layout_section(section_id):
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        section = WebsiteLayout.query.get_or_404(section_id)
        data = request.json
        
        section.section_name = data.get('section_name', section.section_name)
        section.section_type = data.get('section_type', section.section_type)
        section.content = data.get('content', section.content)
        section.settings = data.get('settings', section.settings)
        section.is_active = data.get('is_active', section.is_active)
        section.sort_order = data.get('sort_order', section.sort_order)
        
        db.session.commit()
        return jsonify(section.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/layout/<int:section_id>', methods=['DELETE'])
@jwt_required()
def delete_layout_section(section_id):
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        section = WebsiteLayout.query.get_or_404(section_id)
        db.session.delete(section)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Site Settings Management
@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_site_settings():
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        settings = SiteSettings.query.all()
        return jsonify([setting.to_dict() for setting in settings])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/settings', methods=['POST'])
@jwt_required()
def create_site_setting():
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        data = request.json
        setting = SiteSettings(
            key=data['key'],
            value=data.get('value'),
            description=data.get('description')
        )
        
        db.session.add(setting)
        db.session.commit()
        return jsonify(setting.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/settings/<int:setting_id>', methods=['PUT'])
@jwt_required()
def update_site_setting(setting_id):
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        setting = SiteSettings.query.get_or_404(setting_id)
        data = request.json
        
        setting.key = data.get('key', setting.key)
        setting.value = data.get('value', setting.value)
        setting.description = data.get('description', setting.description)
        
        db.session.commit()
        return jsonify(setting.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/settings/<int:setting_id>', methods=['DELETE'])
@jwt_required()
def delete_site_setting(setting_id):
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        setting = SiteSettings.query.get_or_404(setting_id)
        db.session.delete(setting)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Bulk operations
@admin_bp.route('/products/bulk-update', methods=['POST'])
@jwt_required()
def bulk_update_products():
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        data = request.json
        product_ids = data.get('product_ids', [])
        updates = data.get('updates', {})
        
        if not product_ids:
            return jsonify({'error': 'No product IDs provided'}), 400
        
        # Update products
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        for product in products:
            for key, value in updates.items():
                if hasattr(product, key):
                    setattr(product, key, value)
        
        db.session.commit()
        return jsonify({
            'message': f'Updated {len(products)} products',
            'updated_count': len(products)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/orders/bulk-update', methods=['POST'])
@jwt_required()
def bulk_update_orders():
    try:
        is_admin, user_or_response, status = require_admin()
        if not is_admin:
            return user_or_response, status
        
        data = request.json
        order_ids = data.get('order_ids', [])
        updates = data.get('updates', {})
        
        if not order_ids:
            return jsonify({'error': 'No order IDs provided'}), 400
        
        # Update orders
        orders = Order.query.filter(Order.id.in_(order_ids)).all()
        for order in orders:
            for key, value in updates.items():
                if hasattr(order, key):
                    setattr(order, key, value)
        
        db.session.commit()
        return jsonify({
            'message': f'Updated {len(orders)} orders',
            'updated_count': len(orders)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

