from flask import Blueprint, render_template, abort
from ..models import Page

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/p/<slug>')
def public_page(slug):
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        abort(404)
    products = page.owner.products
    return render_template('page.html', page=page, products=products)
