from flask import Blueprint, render_template, abort
from ..models import Page

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/p/<slug>')
def public_page(slug):
    page = Page.query.filter_by(slug=slug).first()
    if not page:
        abort(404)
    # load products for owner
    products = page.owner.products
    return render_template('page.html', page=page, products=products)
    return redirect(url_for('products.dashboard', page_id=page_id))
