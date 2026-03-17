from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, VerificationCode
from email_service import send_verification_email, generate_code
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
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Пароль должен быть не менее 6 символов', 'error')
            return redirect(url_for('auth.register'))
        
        # Проверка на существование
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким логином уже существует', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован', 'error')
            return redirect(url_for('auth.register'))
        
        # Генерируем код
        code = generate_code()
        
        # Сохраняем в сессию
        session['pending_registration'] = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': role
        }
        
        try:
            # Удаляем старые коды для этого email
            old_codes = VerificationCode.query.filter_by(email=email, is_used=False).all()
            for old in old_codes:
                db.session.delete(old)
            
            # Сохраняем новый код
            verification = VerificationCode(
                email=email,
                code=code,
                username=username,
                password_hash=generate_password_hash(password),
                role=role,
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            db.session.add(verification)
            
            # 🔥 Сохраняем письмо во внутреннюю почту
            send_verification_email(email, code, username)
            
            db.session.commit()
            
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка регистрации. Попробуйте другие данные.', 'error')
            return redirect(url_for('auth.register'))
        
        flash('Код подтверждения отправлен! Проверьте Почту Cafe (порт 5001)', 'success')
        return redirect(url_for('auth.verify_email'))
    
    return render_template('register.html')

@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if 'pending_registration' not in session:
        flash('Сначала заполните форму регистрации', 'error')
        return redirect(url_for('auth.register'))
    
    email = session['pending_registration']['email']
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        
        verification = VerificationCode.query.filter_by(
            email=email, 
            code=code, 
            is_used=False
        ).first()
        
        if not verification:
            flash('Неверный код подтверждения', 'error')
            return redirect(url_for('auth.verify_email'))
        
        if verification.is_expired():
            try:
                db.session.delete(verification)
                db.session.commit()
            except:
                db.session.rollback()
            
            flash('Код истёк. Зарегистрируйтесь заново', 'error')
            session.pop('pending_registration', None)
            return redirect(url_for('auth.register'))
        
        try:
            # Финальная проверка
            if User.query.filter_by(email=email).first():
                flash('Этот email уже зарегистрирован', 'error')
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
            flash('Ошибка: такие данные уже существуют.', 'error')
            session.pop('pending_registration', None)
            return redirect(url_for('auth.register'))
        
        # 🔥 ОЧИЩАЕМ сессию и ПЕРЕБРАСЫВАЕМ НА ВХОД
        session.pop('pending_registration', None)
        
        flash('✅ Email подтверждён! Теперь войдите в систему.', 'success')
        return redirect(url_for('auth.login'))  # ← ПЕРЕБРОС НА СТРАНИЦУ ВХОДА!
    
    return render_template('verify_email.html', email=email)

@auth_bp.route('/resend-code', methods=['POST'])
def resend_code():
    if 'pending_registration' not in session:
        flash('Сначала заполните форму регистрации', 'error')
        return redirect(url_for('auth.register'))
    
    email = session['pending_registration']['email']
    username = session['pending_registration']['username']
    code = generate_code()
    
    try:
        old = VerificationCode.query.filter_by(email=email, is_used=False).first()
        if old:
            db.session.delete(old)
        
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
        
        send_verification_email(email, code, username)
        
    except IntegrityError:
        db.session.rollback()
        flash('Ошибка при отправке кода.', 'error')
        return redirect(url_for('auth.register'))
    
    flash('Новый код отправлен! Проверьте Почту Cafe.', 'success')
    return redirect(url_for('auth.verify_email'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
