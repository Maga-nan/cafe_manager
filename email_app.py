from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from datetime import datetime
import os

# 🔥 Указываем папку с шаблонами почты
app = Flask(__name__, template_folder='email_templates')
app.config['SECRET_KEY'] = 'dev-secret-key-email'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модели (дублируем из models.py для автономности)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='cashier')
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('inbox'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = email
            session['username'] = user.username
            flash(f'Вход выполнен как {user.username}', 'success')
            return redirect(url_for('inbox'))
        else:
            flash('Неверный email или пароль', 'error')
    
    return render_template('email_login.html')

@app.route('/inbox')
def inbox():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    emails = Email.query.filter_by(recipient_email=session['email']).order_by(Email.sent_at.desc()).all()
    return render_template('email_inbox.html', emails=emails, username=session.get('username', ''))

@app.route('/email/<int:email_id>')
def view_email(email_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = Email.query.get_or_404(email_id)
    
    if email.recipient_email != session['email']:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('inbox'))
    
    if not email.is_read:
        email.is_read = True
        db.session.commit()
    
    return render_template('email_view.html', email=email)

@app.route('/delete/<int:email_id>', methods=['POST'])
def delete_email(email_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    email = Email.query.get_or_404(email_id)
    
    if email.recipient_email != session['email']:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('inbox'))
    
    db.session.delete(email)
    db.session.commit()
    flash('Письмо удалено', 'success')
    return redirect(url_for('inbox'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('username', None)
    flash('Вы вышли из почты', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5001)
