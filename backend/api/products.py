from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from ..extensions import db
from ..models import Product, Category, ProductCategory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import os

products_bp = Blueprint('products', __name__)


@products_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        if not current_user.page:
            flash('No se encontró tu página. Contacta al soporte.', 'danger')
            return redirect(url_for('auth.login'))

        products = Product.query.filter_by(owner_id=current_user.id).order_by(Product.created_at.desc()).all()

        available_categories = Category.query.filter(
            or_(
                Category.is_default == True,
                Category.owner_id == current_user.id
            )
        ).order_by(Category.is_default.desc(), Category.name).all()

        return render_template('dashboard.html',
                             products=products,
                             available_categories=available_categories)
    except Exception as e:
        flash('Error al cargar el dashboard. Por favor, intenta nuevamente.', 'danger')
        return redirect(url_for('auth.login'))


@products_bp.route('/', methods=['POST'])
@login_required
def create_product():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price', 0)
    quantity = request.form.get('quantity', 0)

    image = request.files.get('image')
    image_url = None
    if image and image.filename:
        filename = secure_filename(image.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image.save(save_path)
        image_url = url_for('static', filename=f'uploads/{filename}', _external=False)

    product = Product()
    product.name = name
    product.description = description
    product.price = price
    product.quantity = quantity
    product.image_url = image_url
    product.owner_id = current_user.id

    db.session.add(product)
    db.session.commit()

    selected_category_ids = request.form.getlist('categories')

    for category_id in selected_category_ids:
        try:
            category_id = int(category_id)
            category = Category.query.filter(
                Category.id == category_id,
                or_(
                    Category.is_default == True,
                    Category.owner_id == current_user.id
                )
            ).first()

            if category:
                product_category = ProductCategory(
                    product_id=product.id,
                    category_id=category.id
                )
                db.session.add(product_category)
        except (ValueError, TypeError):
            continue

    db.session.commit()
    flash('Producto creado exitosamente', 'success')
    return redirect(url_for('products.dashboard'))


@products_bp.route('/api/categories/create', methods=['POST'])
@login_required
def api_create_category():
    try:
        data = request.get_json()
        category_name = data.get('name', '').strip()
        category_description = data.get('description', '').strip()

        if not category_name:
            return jsonify({'error': 'El nombre de la categoría es requerido'}), 400

        existing_category = Category.query.filter_by(
            name=category_name,
            owner_id=current_user.id
        ).first()

        if existing_category:
            return jsonify({'error': f'Ya tienes una categoría llamada "{category_name}"'}), 400

        new_category = Category(
            name=category_name,
            description=category_description if category_description else None,
            owner_id=current_user.id,
            is_default=False
        )

        db.session.add(new_category)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Categoría "{category_name}" creada exitosamente',
            'category': {
                'id': new_category.id,
                'name': new_category.name,
                'description': new_category.description
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear la categoría: {str(e)}'}), 500


@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    p = Product.query.get_or_404(product_id)
    if p.owner_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('products.dashboard'))

    if request.method == 'GET':
        available_categories = Category.query.filter(
            or_(
                Category.is_default == True,
                Category.owner_id == current_user.id
            )
        ).order_by(Category.is_default.desc(), Category.name).all()

        return render_template('edit_product.html',
                             product=p,
                             available_categories=available_categories)

    try:
        incoming_version = int(request.form.get('version', p.version))
    except Exception:
        incoming_version = p.version

    if incoming_version != p.version:
        flash('El producto fue modificado por otra sesión. Recarga y vuelve a intentar.', 'danger')
        return redirect(url_for('products.dashboard'))

    p.name = request.form.get('name', p.name)
    p.description = request.form.get('description', p.description)
    p.price = request.form.get('price', p.price)
    p.quantity = request.form.get('quantity', p.quantity)

    image = request.files.get('image')
    if image and image.filename:
        filename = secure_filename(image.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image.save(save_path)
        p.image_url = url_for('static', filename=f'uploads/{filename}')

    ProductCategory.query.filter_by(product_id=p.id).delete()

    selected_category_ids = request.form.getlist('categories')

    for category_id in selected_category_ids:
        try:
            category_id = int(category_id)
            category = Category.query.filter(
                Category.id == category_id,
                or_(
                    Category.is_default == True,
                    Category.owner_id == current_user.id
                )
            ).first()

            if category:
                product_category = ProductCategory(
                    product_id=p.id,
                    category_id=category.id
                )
                db.session.add(product_category)
        except (ValueError, TypeError):
            continue

    p.version = p.version + 1
    db.session.commit()
    flash('Producto actualizado exitosamente', 'success')
    return redirect(url_for('products.dashboard'))


@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    if p.owner_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    db.session.delete(p)
    db.session.commit()
    flash('Producto eliminado', 'success')
    return redirect(url_for('products.dashboard'))


@products_bp.route('/<int:product_id>/view')
def view_product(product_id):
    product = Product.query.get_or_404(product_id)

    return render_template('product_detail.html',
                         product=product,
                         page=product.owner.page)
