from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.product import Product, Category, ProductImage
from sqlalchemy import or_

product_bp = Blueprint('product', __name__)

# Category routes
@product_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.json
        category = Category(
            name=data['name'],
            slug=data['slug'],
            description=data.get('description'),
            icon=data.get('icon')
        )
        
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        category = Category.query.get_or_404(category_id)
        data = request.json
        
        category.name = data.get('name', category.name)
        category.slug = data.get('slug', category.slug)
        category.description = data.get('description', category.description)
        category.icon = data.get('icon', category.icon)
        
        db.session.commit()
        return jsonify(category.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Product routes
@product_bp.route('/products', methods=['GET'])
def get_products():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search', '')
        featured = request.args.get('featured', type=bool)
        status = request.args.get('status', 'active')
        
        query = Product.query
        
        # Filter by category
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # Filter by status
        if status:
            query = query.filter(Product.status == status)
        
        # Filter by featured
        if featured is not None:
            query = query.filter(Product.featured == featured)
        
        # Search functionality
        if search:
            query = query.filter(
                or_(
                    Product.title.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%'),
                    Product.sku.ilike(f'%{search}%')
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Product.created_at.desc())
        
        # Paginate results
        products = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.json
        product = Product(
            category_id=data['category_id'],
            title=data['title'],
            description=data.get('description'),
            price=data.get('price'),
            image_url=data.get('image_url'),
            status=data.get('status', 'active'),
            featured=data.get('featured', False),
            sku=data.get('sku'),
            stock_quantity=data.get('stock_quantity', 0),
            weight=data.get('weight'),
            dimensions=data.get('dimensions'),
            meta_title=data.get('meta_title'),
            meta_description=data.get('meta_description')
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Add product images if provided
        if data.get('images'):
            for img_data in data['images']:
                image = ProductImage(
                    product_id=product.id,
                    image_url=img_data['image_url'],
                    alt_text=img_data.get('alt_text'),
                    sort_order=img_data.get('sort_order', 0),
                    is_primary=img_data.get('is_primary', False)
                )
                db.session.add(image)
            db.session.commit()
        
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        product = Product.query.get_or_404(product_id)
        data = request.json
        
        # Update product fields
        product.category_id = data.get('category_id', product.category_id)
        product.title = data.get('title', product.title)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.image_url = data.get('image_url', product.image_url)
        product.status = data.get('status', product.status)
        product.featured = data.get('featured', product.featured)
        product.sku = data.get('sku', product.sku)
        product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
        product.weight = data.get('weight', product.weight)
        product.dimensions = data.get('dimensions', product.dimensions)
        product.meta_title = data.get('meta_title', product.meta_title)
        product.meta_description = data.get('meta_description', product.meta_description)
        
        db.session.commit()
        return jsonify(product.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Featured products
@product_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    try:
        limit = request.args.get('limit', 8, type=int)
        products = Product.query.filter(
            Product.featured == True,
            Product.status == 'active'
        ).limit(limit).all()
        
        return jsonify([product.to_dict() for product in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

