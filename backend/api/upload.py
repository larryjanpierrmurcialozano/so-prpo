from flask import Blueprint, request, current_app, jsonify, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename
import os

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'no file'}), 400
    filename = secure_filename(f.filename)
    dest = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    f.save(dest)
    # For dev, return a relative URL pointing to the uploads mount
    url = url_for('static', filename=f'uploads/{filename}', _external=False)
    return jsonify({'url': url})
