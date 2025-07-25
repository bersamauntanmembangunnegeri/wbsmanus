from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.models.user import User, db
from src.models.product import Product
from src.models.order import Order, OrderItem, ShoppingCart
from datetime import datetime
import uuid

order_bp = Blueprint('order', __name__)

# Shopping Cart routes
@order_bp.route('/cart', methods=['GET'])
def get_cart():
    try:
        # Get cart items for logged-in user or session
        cart_items = []
        
        # Try to get user from JWT token
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                cart_items = ShoppingCart.query.filter_by(user_id=user_id).all()
        except:
            user_id = None
        
        # If no user, use session ID
        if not user_id:
            session_id = session.get('cart_session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['cart_session_id'] = session_id
            cart_items = ShoppingCart.query.filter_by(session_id=session_id).all()
        
        return jsonify([item.to_dict() for item in cart_items])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.json
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        
        # Check if product exists and has stock
        product = Product.query.get_or_404(product_id)
        if product.stock_quantity < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Get user or session
        user_id = None
        session_id = None
        
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        if not user_id:
            session_id = session.get('cart_session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['cart_session_id'] = session_id
        
        # Check if item already in cart
        if user_id:
            cart_item = ShoppingCart.query.filter_by(
                user_id=user_id, 
                product_id=product_id
            ).first()
        else:
            cart_item = ShoppingCart.query.filter_by(
                session_id=session_id, 
                product_id=product_id
            ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock_quantity:
                cart_item.quantity = product.stock_quantity
        else:
            # Create new cart item
            cart_item = ShoppingCart(
                user_id=user_id,
                session_id=session_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify(cart_item.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    try:
        data = request.json
        quantity = data.get('quantity', 1)
        
        cart_item = ShoppingCart.query.get_or_404(item_id)
        
        # Check stock
        if cart_item.product.stock_quantity < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        return jsonify(cart_item.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    try:
        cart_item = ShoppingCart.query.get_or_404(item_id)
        db.session.delete(cart_item)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/cart/clear', methods=['DELETE'])
def clear_cart():
    try:
        # Get user or session
        user_id = None
        session_id = None
        
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        if not user_id:
            session_id = session.get('cart_session_id')
        
        # Delete cart items
        if user_id:
            ShoppingCart.query.filter_by(user_id=user_id).delete()
        elif session_id:
            ShoppingCart.query.filter_by(session_id=session_id).delete()
        
        db.session.commit()
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Order routes
@order_bp.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        
        # Get cart items
        user_id = None
        session_id = None
        
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        if not user_id:
            session_id = session.get('cart_session_id')
        
        # Get cart items
        if user_id:
            cart_items = ShoppingCart.query.filter_by(user_id=user_id).all()
        elif session_id:
            cart_items = ShoppingCart.query.filter_by(session_id=session_id).all()
        else:
            return jsonify({'error': 'No cart items found'}), 400
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Calculate total
        total_price = 0
        for item in cart_items:
            total_price += float(item.product.price) * item.quantity
        
        # Create order (using legacy format for compatibility)
        # For now, create one order per cart item (legacy structure)
        orders = []
        for item in cart_items:
            order = Order(
                user_id=user_id,
                product_id=item.product_id,
                vendor_id=1,  # Default vendor
                customer_email=data['customer_email'],
                quantity=item.quantity,
                unit_price=item.product.price,
                total_price=float(item.product.price) * item.quantity,
                payment_method=data['payment_method'],
                coupon_code=data.get('coupon_code'),
                subscribe_newsletter=data.get('subscribe_newsletter', False),
                status='pending',
                shipping_address=data.get('shipping_address'),
                billing_address=data.get('billing_address'),
                order_notes=data.get('order_notes')
            )
            db.session.add(order)
            orders.append(order)
        
        # Clear cart
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'orders': [order.to_dict() for order in orders],
            'total_amount': total_price
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role == 'admin':
            # Admin can see all orders
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            status = request.args.get('status')
            
            query = Order.query
            if status:
                query = query.filter(Order.status == status)
            
            orders = query.order_by(Order.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'orders': [order.to_dict() for order in orders.items],
                'total': orders.total,
                'pages': orders.pages,
                'current_page': page
            })
        else:
            # Regular users see only their orders
            orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
            return jsonify([order.to_dict() for order in orders])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order = Order.query.get_or_404(order_id)
        
        # Check access permissions
        if user.role != 'admin' and order.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(order.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        order = Order.query.get_or_404(order_id)
        data = request.json
        
        # Update order fields
        order.status = data.get('status', order.status)
        order.tracking_number = data.get('tracking_number', order.tracking_number)
        order.order_notes = data.get('order_notes', order.order_notes)
        
        # Update timestamps based on status
        if data.get('status') == 'shipped' and not order.shipped_at:
            order.shipped_at = datetime.utcnow()
        elif data.get('status') == 'delivered' and not order.delivered_at:
            order.delivered_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(order.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

