from flask import Blueprint, render_template, request, jsonify
from models import db, VerificationCode
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/codes')
def admin_codes():
    """
    Страница с кодами подтверждения (открывается в отдельном окне)
    Показывает все неподтверждённые регистрации
    """
    # Получаем все неиспользованные коды
    codes = VerificationCode.query.filter_by(is_used=False).order_by(VerificationCode.created_at.desc()).all()
    
    # Фильтруем только не истёкшие
    active_codes = [c for c in codes if not c.is_expired()]
    
    return render_template('admin_codes.html', codes=active_codes)

@admin_bp.route('/admin/codes/api')
def admin_codes_api():
    """API для автообновления окна кодов"""
    codes = VerificationCode.query.filter_by(is_used=False).all()
    active_codes = [c for c in codes if not c.is_expired()]
    
    return jsonify([{
        'email': c.email,
        'username': c.username,
        'code': c.code,
        'expires_in': int((c.expires_at - datetime.utcnow()).total_seconds()),
        'created': c.created_at.strftime('%H:%M:%S')
    } for c in active_codes])
