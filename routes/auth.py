from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, VerificationCode
from email_service import save_verification_code, generate_code
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_verified:
                flash('Подтвердите email перед входом', 'error')
                return redirect(url_for('auth.login'))
            login_user(user)
            return redirect(url_for('index_dashboard'))
        else:
            flash('Неверный логин или пароль', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'cashier')
        
        # Проверки
        if not username or not email or not password:
            flash('Все поля обязательны', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Пароль должен быть не менее 6 символов', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким логином уже существует', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован', 'error')
            return redirect(url_for('auth.register'))
        
        # Генерируем код
        code = generate_code()
        password_hash = generate_password_hash(password)
        
        # Сохраняем в сессию
        session['pending_registration'] = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role
        }
        
        try:
            # Сохраняем код в базу (будет виден в /admin/codes)
            save_verification_code(email, code, username, password_hash, role)
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка регистрации', 'error')
            return redirect(url_for('auth.register'))
        
        flash(f'✅ Регистрация! Код: {code} | Откройте окно кодов ↗', 'success')
        return redirect(url_for('auth.verify_email', email=email))
    
    return render_template('register.html')

@auth_bp.route('/verify-email')
@auth_bp.route('/verify-email/<email>', methods=['GET', 'POST'])
def verify_email(email=None):
    if 'pending_registration' not in session:
        flash('Сначала зарегистрируйтесь', 'error')
        return redirect(url_for('auth.register'))
    
    if email is None:
        email = session['pending_registration']['email']
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        
        verification = VerificationCode.query.filter_by(
            email=email, 
            code=code, 
            is_used=False
        ).first()
        
        if not verification:
            flash('Неверный код', 'error')
            return redirect(url_for('auth.verify_email', email=email))
        
        if verification.is_expired():
            flash('Код истёк. Зарегистрируйтесь заново', 'error')
            session.pop('pending_registration', None)
            return redirect(url_for('auth.register'))
        
        try:
            # Финальная проверка
            if User.query.filter_by(email=email).first():
                flash('Email уже зарегистрирован', 'error')
                session.pop('pending_registration', None)
                return redirect(url_for('auth.register'))
            
            # Создаём пользователя
            user = User(
                username=session['pending_registration']['username'],
                email=email,
                password_hash=session['pending_registration']['password_hash'],
                role=session['pending_registration']['role'],
                is_verified=True
            )
            db.session.add(user)
            verification.is_used = True
            db.session.commit()
            
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка: данные уже существуют', 'error')
            session.pop('pending_registration', None)
            return redirect(url_for('auth.register'))
        
        session.pop('pending_registration', None)
        flash('✅ Подтверждено! Войдите в систему.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('verify_email.html', email=email)

@auth_bp.route('/resend-code', methods=['POST'])
def resend_code():
    if 'pending_registration' not in session:
        flash('Сначала зарегистрируйтесь', 'error')
        return redirect(url_for('auth.register'))
    
    email = session['pending_registration']['email']
    username = session['pending_registration']['username']
    code = generate_code()
    
    try:
        save_verification_code(
            email, code, username,
            session['pending_registration']['password_hash'],
            session['pending_registration']['role']
        )
        flash(f'Новый код: {code} | Проверьте окно кодов ↗', 'success')
    except:
        flash('Ошибка отправки кода', 'error')
    
    return redirect(url_for('auth.verify_email', email=email))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
