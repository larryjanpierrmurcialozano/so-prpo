from flask import Blueprint, render_template, request, jsonify
from backend.models import User, Page, Product, Category
from backend.extensions import db
from sqlalchemy import or_, and_

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def search_page():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')  # all, users, pages, products, categories
    category_id = request.args.get('category', '')
    
    results = {
        'query': query,
        'search_type': search_type,
        'users': [],
        'pages': [],
        'products': [],
        'categories': []
    }

    all_categories = Category.query.all()
    
    if query:
        if search_type in ['all', 'users']:
            users_query = User.query.filter(
                or_(
                    User.username.contains(query),
                    User.email.contains(query)
                )
            )

            if category_id:
                try:
                    users_query = users_query.join(User.products).join(Product.categories).filter(
                        Category.id == int(category_id)
                    ).distinct()
                except (ValueError, TypeError):
                    pass

            users = users_query.limit(20).all()
            results['users'] = users

        if search_type in ['all', 'pages']:
            pages_query = Page.query.join(Page.owner).filter(
                or_(
                    Page.title.ilike(f'%{query}%'),
                    Page.slug.ilike(f'%{query}%'),
                    User.username.ilike(f'%{query}%')
                )
            )

            if category_id:
                try:
                    pages_query = pages_query.join(User.products).join(Product.categories).filter(
                        Category.id == int(category_id)
                    ).distinct()
                except (ValueError, TypeError):
                    pass

            pages = pages_query.limit(20).all()
            results['pages'] = pages

        if search_type in ['all', 'products']:
            product_query = Product.query.join(Product.owner).filter(
                or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.description.ilike(f'%{query}%'),
                    User.username.ilike(f'%{query}%')
                )
            )

            if category_id:
                try:
                    product_query = product_query.join(Product.categories).filter(
                        Category.id == int(category_id)
                    )
                except (ValueError, TypeError):
                    pass

            products = product_query.limit(50).all()
            results['products'] = products

        if search_type in ['all', 'categories']:
            categories = Category.query.filter(
                or_(
                    Category.name.contains(query),
                    Category.description.contains(query)
                )
            ).limit(20).all()
            results['categories'] = categories

    elif category_id:
        if search_type in ['all', 'users']:
            try:
                users = User.query.join(User.products).join(Product.categories).filter(
                    Category.id == int(category_id)
                ).distinct().limit(20).all()
                results['users'] = users
            except (ValueError, TypeError):
                pass

        if search_type in ['all', 'pages']:
            try:
                pages = Page.query.join(Page.owner).join(User.products).join(Product.categories).filter(
                    Category.id == int(category_id)
                ).distinct().limit(20).all()
                results['pages'] = pages
            except (ValueError, TypeError):
                pass

        if search_type in ['all', 'products']:
            try:
                products = Product.query.join(Product.categories).filter(
                    Category.id == int(category_id)
                ).limit(50).all()
                results['products'] = products
            except (ValueError, TypeError):
                pass

    if not query and not category_id:
        if search_type == 'pages' or search_type == 'all':
            all_pages = Page.query.limit(50).all()
            results['pages'] = all_pages

        if search_type == 'products':
            all_products = Product.query.limit(50).all()
            results['products'] = all_products

        if search_type == 'users':
            all_users = User.query.limit(20).all()
            results['users'] = all_users

    return render_template('search_advanced.html',
                         results=results,
                         all_categories=all_categories,
                         selected_category=category_id)

@search_bp.route('/api/categories/search')
def search_categories_api():
    query = request.args.get('q', '')
    user_id = request.args.get('user_id')
    
    categories_query = Category.query
    
    if query:
        categories_query = categories_query.filter(
            Category.name.contains(query)
        )

    if user_id:
        categories_query = categories_query.filter(
            or_(
                Category.is_default == True,
                Category.owner_id == user_id
            )
        )
    else:
        categories_query = categories_query.filter(Category.is_default == True)
    
    categories = categories_query.limit(10).all()
    
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'description': cat.description or '',
        'is_custom': not cat.is_default
    } for cat in categories])

@search_bp.route('/api/categories/create', methods=['POST'])
def create_category_api():
    from flask_login import current_user

    if not current_user.is_authenticated:
        return jsonify({'error': 'No autenticado', 'success': False}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos', 'success': False}), 400

        name = data.get('name', '').strip()
        description = data.get('description', '').strip()

        if not name:
            return jsonify({'error': 'El nombre de la categoría es requerido', 'success': False}), 400

        # Verificar si ya existe
        existing = Category.query.filter(
            and_(
                Category.name == name,
                or_(
                    Category.is_default == True,
                    Category.owner_id == current_user.id
                )
            )
        ).first()

        if existing:
            return jsonify({'error': f'Ya tienes una categoría llamada "{name}"', 'success': False}), 400

        # Crear la nueva categoría
        category = Category(
            name=name,
            description=description if description else None,
            is_default=False,
            owner_id=current_user.id
        )

        db.session.add(category)
        db.session.flush()  # Obtener el ID antes del commit

        # Preparar respuesta con los datos
        category_data = {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Categoría "{name}" creada exitosamente',
            'category': category_data
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error al crear categoría: {str(e)}")  # Log para depuración
        return jsonify({'error': f'Error al crear la categoría: {str(e)}', 'success': False}), 500
