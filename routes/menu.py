from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, MenuItem

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/')
@login_required
def menu_list():
    items = MenuItem.query.order_by(MenuItem.category, MenuItem.name).all()
    return render_template('menu.html', items=items)

@menu_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.role not in ['manager', 'admin']:
        flash('Недостаточно прав', 'error')
        return redirect(url_for('menu.menu_list'))
    
    if request.method == 'POST':
        item = MenuItem(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            category=request.form.get('category', 'Основное'),
            is_available=True
        )
        db.session.add(item)
        db.session.commit()
        
        flash('Блюдо добавлено', 'success')
        return redirect(url_for('menu.menu_list'))
    
    return render_template('add_menu_item.html')

@menu_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    if current_user.role not in ['manager', 'admin']:
        flash('Недостаточно прав', 'error')
        return redirect(url_for('menu.menu_list'))
    
    item = MenuItem.query.get_or_404(item_id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.price = float(request.form.get('price'))
        item.category = request.form.get('category')
        item.is_available = request.form.get('is_available') == 'on'
        db.session.commit()
        
        flash('Блюдо обновлено', 'success')
        return redirect(url_for('menu.menu_list'))
    
    return render_template('edit_menu_item.html', item=item)

@menu_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    if current_user.role not in ['manager', 'admin']:
        flash('Недостаточно прав', 'error')
        return redirect(url_for('menu.menu_list'))
    
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    flash('Блюдо удалено', 'success')
    return redirect(url_for('menu.menu_list'))
