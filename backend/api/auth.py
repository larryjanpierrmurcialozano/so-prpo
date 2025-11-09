from flask import Blueprint, request, redirect, url_for, render_template, flash
from ..extensions import db
from ..models import User, Page
from flask_login import login_user, login_required, logout_user, current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return render_template('already_logged_in.html', current_user=current_user)

    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')

            if not username or not email or not password:
                flash('Por favor, rellena todos los campos', 'danger')
                return render_template('register.html')

            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'danger')
                return render_template('register.html')

            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash('El usuario o email ya existe. Intenta con otro.', 'danger')
                return render_template('register.html')

            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            slug = username.lower().replace(' ', '-').replace('_', '-')
            page = Page()
            page.title = username
            page.slug = slug
            page.owner = user
            db.session.add(page)
            db.session.commit()

            login_user(user, remember=True)
            flash(f'¡Bienvenido {username}! Tu cuenta ha sido creada exitosamente.', 'success')
            return redirect(url_for('products.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash ('Error al crear la cuenta. Por favor, intenta nuevamente.',  'danger')
            return render_template('register.html')
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('already_logged_in.html', current_user=current_user)

    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                flash('Por favor, ingresa tu usuario y contraseña', 'danger')
                return render_template('login.html')

            user = User.query.filter_by(username=username).first()

            if not user:
                flash('Usuario no encontrado. Verifica tus datos o regístrate.', 'danger')
                return render_template('login.html')

            if not user.check_password(password):
                flash('Contraseña incorrecta. Intenta nuevamente.', 'danger')
                return render_template('login.html')

            # Actualizar último inicio de sesión
            from datetime import datetime, timezone
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            login_user(user, remember=True)
            flash(f'¡Bienvenido de nuevo, {user.username}!', 'success')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)

            return redirect(url_for('products.dashboard'))

        except Exception as e:
            flash('Error al iniciar sesión. Por favor, intenta nuevamente.', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f'Has cerrado sesión correctamente.  usuario cerrado: {username}!', 'success')
    return redirect(url_for('auth.login'))
