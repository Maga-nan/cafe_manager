from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, VerificationCode
from email_service import send_verification_email, generate_code
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
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
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'cashier')
        
        # Проверки
        if User.query.filter_by(username=username).first():
            flash('Пользователь уже существует', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Пароль должен быть не менее 6 символов', 'error')
            return redirect(url_for('auth.register'))
        
        # Генерируем код подтверждения
        code = generate_code()
        
        # Сохраняем временные данные в сессии
        session['pending_registration'] = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': role
        }
        session['pending_code'] = code
        
        # Сохраняем код в БД
        verification = VerificationCode(
            email=email,
            code=code,
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(verification)
        db.session.commit()
        
        # Отправляем email
        if send_verification_email(email, code, username):
            flash('Код подтверждения отправлен на email', 'success')
            return redirect(url_for('auth.verify_email'))
        else:
            flash('Ошибка отправки email. Попробуйте позже.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if 'pending_registration' not in session:
        flash('Сначала заполните форму регистрации', 'error')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        email = session['pending_registration']['email']
        
        # Ищем код в БД
        verification = VerificationCode.query.filter_by(
            email=email, 
            code=code, 
            is_used=False
        ).first()
        
        if not verification:
            flash('Неверный код подтверждения', 'error')
            return redirect(url_for('auth.verify_email'))
        
        if verification.is_expired():
            flash('Код истёк. Зарегистрируйтесь заново', 'error')
            session.pop('pending_registration', None)
            session.pop('pending_code', None)
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
        
        # Помечаем код как использованный
        verification.is_used = True
        db.session.commit()
        
        # Очищаем сессию
        session.pop('pending_registration', None)
        session.pop('pending_code', None)
        
        flash('Email подтверждён! Теперь войдите', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('verify_email.html', email=session.get('pending_registration', {}).get('email', ''))

@auth_bp.route('/resend-code', methods=['POST'])
def resend_code():
    if 'pending_registration' not in session:
        flash('Сначала заполните форму регистрации', 'error')
        return redirect(url_for('auth.register'))
    
    email = session['pending_registration']['email']
    username = session['pending_registration']['username']
    code = generate_code()
    
    # Обновляем код в БД
    old_verification = VerificationCode.query.filter_by(
        email=email, 
        is_used=False
    ).first()
    if old_verification:
        db.session.delete(old_verification)
    
    verification = VerificationCode(
        email=email,
        code=code,
        username=username,
        password_hash=session['pending_registration']['password_hash'],
        role=session['pending_registration']['role'],
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.session.add(verification)
    db.session.commit()
    
    session['pending_code'] = code
    
    if send_verification_email(email, code, username):
        flash('Новый код отправлен', 'success')
    else:
        flash('Ошибка отправки email', 'error')
    
    return redirect(url_for('auth.verify_email'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
