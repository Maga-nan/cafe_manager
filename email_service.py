from flask_mail import Mail, Message
import random
import string
from datetime import datetime
from models import db

# Создаём модель Email, если её нет
class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def generate_code(length=6):
    """Генерирует случайный код из цифр"""
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email, code, username):
    """Отправляет письмо с кодом подтверждения (сохраняет в базу)"""
    try:
        # Создаём HTML версию письма
        html_body = f'''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2d3436;">☕ Cafe Manager</h2>
            <p>Привет, <strong>{username}</strong>!</p>
            <p>Спасибо за регистрацию в системе Cafe Manager.</p>
            <p>Ваш код подтверждения:</p>
            <div class="code-box" style="background: #0984e3; color: white; padding: 20px; 
                        text-align: center; font-size: 24px; 
                        letter-spacing: 5px; border-radius: 5px; 
                        display: inline-block;">
                <strong>{code}</strong>
            </div>
            <p>Код действителен в течение <strong>10 минут</strong>.</p>
            <p>Если вы не регистрировались, просто проигнорируйте это письмо.</p>
            <hr style="border: none; border-top: 1px solid #dfe6e9; margin: 20px 0;">
            <p style="color: #636e72; font-size: 12px;">
                © 2024 Cafe Manager. Все права защищены.
            </p>
        </body>
        </html>
        '''
        
        # Сохраняем письмо в базу данных
        email_record = Email(
            recipient_email=email,
            subject='☕ Подтверждение регистрации - Cafe Manager',
            body=html_body,
            sent_at=datetime.utcnow()
        )
        db.session.add(email_record)
        db.session.commit()
        
        print(f"✅ Письмо с кодом {code} сохранено в почту для {email}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сохранения email: {e}")
        db.session.rollback()
        return False
