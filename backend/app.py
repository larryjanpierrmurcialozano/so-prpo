import os
from flask import Flask, render_template, flash, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

from .config import Config
from .extensions import db, migrate, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")
    app.config.from_object(config_class)

    static_uploads = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'uploads')
    uploads_path = os.path.abspath(static_uploads)
    os.makedirs(uploads_path, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = uploads_path

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('auth.login'))

    from .api.auth import auth_bp
    from .api.products import products_bp
    from .api.pages import pages_bp
    from .api.upload import upload_bp
    from .api.settings import settings_bp
    from .api.search_advanced import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(pages_bp)
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(settings_bp)
    app.register_blueprint(search_bp)

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/support")
    def support():
        return render_template('support.html')

    return app
