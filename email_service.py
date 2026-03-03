from flask_mail import Mail, Message
import random
import string

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def generate_code(length=6):
    """Генерирует случайный код из цифр"""
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email, code, username):
    """Отправляет письмо с кодом подтверждения"""
    try:
        msg = Message(
            subject='☕ Подтверждение регистрации - Cafe Manager',
            sender='Cafe Manager <noreply@cafemanager.com>',
            recipients=[email]
        )
        msg.html = f'''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2d3436;">☕ Cafe Manager</h2>
            <p>Привет, <strong>{username}</strong>!</p>
            <p>Спасибо за регистрацию в системе Cafe Manager.</p>
            <p>Ваш код подтверждения:</p>
            <div style="background: #0984e3; color: white; padding: 20px; 
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
        msg.body = f'''
Cafe Manager - Подтверждение регистрации

Привет, {username}!

Ваш код подтверждения: {code}

Код действителен в течение 10 минут.

Если вы не регистрировались, просто проигнорируйте это письмо.
        '''
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False
