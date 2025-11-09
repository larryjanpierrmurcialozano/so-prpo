from datetime import datetime, timezone
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Numeric, String


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)

    page = db.relationship("Page", uselist=False, back_populates="owner", cascade="all, delete-orphan")
    products = db.relationship("Product", back_populates="owner", cascade="all, delete-orphan")
    custom_categories = db.relationship("Category", back_populates="owner", cascade="all, delete-orphan", foreign_keys="Category.owner_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Page(db.Model):
    __tablename__ = "pages"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False, default="Mi Tienda")
    slug = db.Column(db.String(150), unique=True, nullable=False)
    color_bg = db.Column(db.String(7), default="#ffffff")
    color_header = db.Column(db.String(7), default="#667eea")
    color_footer = db.Column(db.String(7), default="#343a40")
    color_text = db.Column(db.String(7), default="#212529")
    logo_url = db.Column(db.String(500), nullable=True)
    logo_size = db.Column(db.Integer, default=60)
    font_size = db.Column(db.Integer, default=16)

    phone_number = db.Column(db.String(20), nullable=True)
    facebook_url = db.Column(db.String(500), nullable=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = db.relationship("User", back_populates="page")


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_default = db.Column(db.Boolean, default=False, nullable=False)  # Para categorías predeterminadas del sistema
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # NULL para categorías globales
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner = db.relationship("User", back_populates="custom_categories")
    products = db.relationship("Product", secondary="product_categories", back_populates="categories")

    def __repr__(self):
        return f'<Category {self.name}>'


class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    version = db.Column(db.Integer, default=1, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner = db.relationship("User", back_populates="products")
    categories = db.relationship("Category", secondary="product_categories", back_populates="products")

    def get_category_names(self):
        return [cat.name for cat in self.categories]
