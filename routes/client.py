from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, MenuItem, Order, OrderItem
from werkzeug.security import generate_password_hash
from datetime import datetime
from sqlalchemy.exc import IntegrityError

client_bp = Blueprint('client', __name__)

@client_bp.route('/client')
def client_home():
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    categories = db.session.query(MenuItem.category).distinct().all()
    return render_template('client_home.html', menu_items=menu_items, categories=categories)

@client_bp.route('/client/register', methods=['GET', 'POST'])
def client_register():
    if current_user.is_authenticated:
        return redirect(url_for('client.client_home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not password:
            flash('Имя и пароль обязательны', 'error')
            return redirect(url_for('client.client_register'))
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('client.client_register'))
        
        if len(password) < 4:
            flash('Пароль должен быть не менее 4 символов', 'error')
            return redirect(url_for('client.client_register'))
        
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя занято', 'error')
            return redirect(url_for('client.client_register'))
        
        if email and User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'error')
            return redirect(url_for('client.client_register'))
        
        try:
            client = User(
                username=username,
                email=email or f'{username}@client.local',
                password_hash=generate_password_hash(password),
                role='client',
                phone=phone,
                is_verified=True
            )
            db.session.add(client)
            db.session.commit()
            
            flash('✅ Регистрация успешна! Теперь войдите.', 'success')
            return redirect(url_for('client.client_login'))
            
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка регистрации. Попробуйте другое имя.', 'error')
    
    return render_template('client_register.html')

@client_bp.route('/client/login', methods=['GET', 'POST'])
def client_login():
    if current_user.is_authenticated:
        return redirect(url_for('client.client_home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username, role='client').first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('client.client_home'))
        else:
            flash('Неверное имя или пароль', 'error')
    
    return render_template('client_login.html')

@client_bp.route('/client/order', methods=['GET', 'POST'])
def client_order():
    if request.method == 'POST':
        cart = request.form.get('cart', '')
        table_number = request.form.get('table_number', '')
        
        if not cart:
            flash('Корзина пуста', 'error')
            return redirect(url_for('client.client_home'))
        
        try:
            import json
            items = json.loads(cart)
            
            order = Order(
                user_id=current_user.id if current_user.is_authenticated else None,
                client_name=current_user.username if current_user.is_authenticated else request.form.get('client_name', 'Гость'),
                client_phone=current_user.phone if current_user.is_authenticated else request.form.get('client_phone', ''),
                table_number=int(table_number) if table_number else None,
                status='new',
                total_amount=0
            )
            db.session.add(order)
            db.session.flush()
            
            total = 0
            for item in items:
                menu_item = MenuItem.query.get(item['id'])
                if menu_item:
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=menu_item.id,
                        quantity=item['quantity'],
                        price=menu_item.price
                    )
                    db.session.add(order_item)
                    total += menu_item.price * item['quantity']
            
            order.total_amount = total
            db.session.commit()
            
            flash(f'✅ Заказ #{order.id} оформлен!', 'success')
            return redirect(url_for('client.client_orders'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {e}', 'error')
    
    return redirect(url_for('client.client_home'))

@client_bp.route('/client/orders')
@login_required
def client_orders():
    if current_user.role != 'client':
        flash('Доступ только для клиентов', 'error')
        return redirect(url_for('client.client_home'))
    
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('client_orders.html', orders=orders)

@client_bp.route('/client/order/<int:order_id>')
@login_required
def client_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('client.client_orders'))
    
    return render_template('client_order_detail.html', order=order)

@client_bp.route('/client/logout')
@login_required
def client_logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('client.client_home'))
