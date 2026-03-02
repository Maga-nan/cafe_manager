from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Order, OrderItem, MenuItem
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/')
@login_required
def orders_list():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    if request.method == 'POST':
        order = Order(user_id=current_user.id, status='new')
        db.session.add(order)
        db.session.commit()
        
        item_ids = request.form.getlist('item_id')
        quantities = request.form.getlist('quantity')
        
        total = 0
        for item_id, qty in zip(item_ids, quantities):
            if qty and int(qty) > 0:
                menu_item = MenuItem.query.get(int(item_id))
                if menu_item:
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=menu_item.id,
                        quantity=int(qty),
                        price=menu_item.price
                    )
                    db.session.add(order_item)
                    total += menu_item.price * int(qty)
        
        order.total_amount = total
        db.session.commit()
        
        flash('Заказ создан успешно!', 'success')
        return redirect(url_for('orders.orders_list'))
    
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    return render_template('create_order.html', menu_items=menu_items)

@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    if current_user.role not in ['manager', 'admin']:
        flash('Недостаточно прав', 'error')
        return redirect(url_for('orders.orders_list'))
    
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status')
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Статус обновлен', 'success')
    return redirect(url_for('orders.orders_list'))

@orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    if current_user.role not in ['manager', 'admin']:
        flash('Недостаточно прав', 'error')
        return redirect(url_for('orders.orders_list'))
    
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    
    flash('Заказ удален', 'success')
    return redirect(url_for('orders.orders_list'))
