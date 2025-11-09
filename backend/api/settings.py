from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Page
from flask_login import login_required, current_user
import os

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET'])
@login_required
def page_settings():
    try:
        if not current_user.page:
            flash('No se encontró tu página. Contacta al soporte.', 'danger')
            return redirect(url_for('products.dashboard'))
        return render_template('settings.html', page=current_user.page)
    except Exception as e:
        flash('Error al cargar la configuración.', 'danger')
        return redirect(url_for('products.dashboard'))


@settings_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    page = current_user.page
    
    page.title = request.form.get('title', page.title)
    page.color_bg = request.form.get('color_bg', page.color_bg)
    page.color_header = request.form.get('color_header', page.color_header)
    page.color_footer = request.form.get('color_footer', page.color_footer)
    page.color_text = request.form.get('color_text', page.color_text)
    page.phone_number = request.form.get('phone_number', '').strip() or None
    page.facebook_url = request.form.get('facebook_url', '').strip() or None

    logo_size = request.form.get('logo_size', page.logo_size)
    try:
        page.logo_size = int(logo_size)
        if page.logo_size < 30:
            page.logo_size = 30
        elif page.logo_size > 200:
            page.logo_size = 200
    except:
        pass

    font_size = request.form.get('font_size', page.font_size)
    try:
        page.font_size = int(font_size)
        if page.font_size < 12:
            page.font_size = 12
        elif page.font_size > 24:
            page.font_size = 24
    except:
        pass

    logo = request.files.get('logo')
    if logo and logo.filename:
        filename = secure_filename(logo.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        logo.save(save_path)
        page.logo_url = url_for('static', filename=f'uploads/{filename}')

    db.session.commit()
    flash('Configuración actualizada exitosamente', 'success')
    return redirect(url_for('settings.page_settings'))


@settings_bp.route('/settings/reset', methods=['POST'])
@login_required
def reset_settings():
    page = current_user.page
    try:
        page.title = "Título por defecto"
        page.color_bg = "#FFFFFF"
        page.color_header = "#000000"
        page.color_footer = "#000000"
        page.color_text = "#333333"
        page.phone_number = None
        page.facebook_url = None
        page.logo_size = 100

        page.logo_url = None

        db.session.commit()
        flash('Configuración de la página restaurada a los valores predeterminados.', 'success')
        return jsonify({'message': 'Configuración restaurada exitosamente.'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al limpiar la configuración.'}), 500


@settings_bp.route('/admin/cleanup/stats', methods=['GET'])
@login_required
def cleanup_stats():
    """Obtener estadísticas de limpieza del sistema"""
    try:
        if current_user.id != 1:
            return jsonify({'error': 'Acceso denegado'}), 403

        from ..cleanup_tasks import get_cleanup_stats
        stats = get_cleanup_stats()

        return jsonify({
            'success': True,
            'data': {
                'inactive_accounts': stats['inactive_accounts'],
                'unused_categories': stats['unused_categories'],
                'last_check': stats['last_check'].isoformat()
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error obteniendo estadísticas: {str(e)}'}), 500


@settings_bp.route('/admin/cleanup/execute', methods=['POST'])
@login_required
def execute_cleanup():
    try:
        if current_user.id != 1:
            return jsonify({'error': 'Acceso denegado'}), 403

        from ..cleanup_tasks import run_full_cleanup

        confirm = request.json.get('confirm', False) if request.is_json else request.form.get('confirm', False)
        if not confirm:
            return jsonify({'error': 'Confirmación requerida para ejecutar la limpieza'}), 400

        results = run_full_cleanup()

        return jsonify({
            'success': True,
            'message': 'Limpieza ejecutada exitosamente',
            'data': {
                'deleted_accounts': results['deleted_accounts'],
                'deleted_categories': results['deleted_categories'],
                'timestamp': results['timestamp'].isoformat()
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error ejecutando limpieza: {str(e)}'}), 500

@settings_bp.route('/settings/clean', methods=['POST'])
@login_required
def clean_settings():
    try:
        page = current_user.page
        if not page:
            return jsonify({'error': 'No se encontró la página del usuario.'}), 404

        page.title = ''
        page.color_bg = ''
        page.color_header = ''
        page.color_footer = ''
        page.color_text = ''
        page.phone_number = None
        page.facebook_url = None
        page.logo_size = 30
        page.logo_url = None

        db.session.commit()
        flash('Configuración de la página restaurada a los valores predeterminados.', 'success')
        return jsonify({'message': 'Configuración restaurada exitosamente.'}), 200
    except Exception as e:
        return jsonify({'error': 'Error al limpiar la configuración.'}), 500
