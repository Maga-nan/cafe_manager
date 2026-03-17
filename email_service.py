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
    """Отправляет письмо с кодом подтверждения на РЕАЛЬНУЮ почту"""
    try:
        msg = Message(
            subject='☕ Подтверждение регистрации - Cafe Manager',
            sender='Cafe Manager <noreply@cafemanager.com>',
            recipients=[email]
        )
        msg.html = f'''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f6fa;">
            <div style="max-width: 600px; margin: 0 auto; background: white; 
                        padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #667eea; text-align: center;">☕ Cafe Manager</h2>
                <p>Привет, <strong>{username}</strong>!</p>
                <p>Спасибо за регистрацию в системе Cafe Manager.</p>
                <p>Ваш код подтверждения:</p>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; 
                            padding: 20px; 
                            text-align: center; 
                            font-size: 32px; 
                            font-weight: bold;
                            letter-spacing: 5px; 
                            border-radius: 8px; 
                            margin: 20px 0;">
                    {code}
                </div>
                
                <p>Код действителен в течение <strong>10 минут</strong>.</p>
                <p style="color: #666; font-size: 14px;">
                    Если вы не регистрировались, просто проигнорируйте это письмо.
                </p>
                <hr style="border: none; border-top: 1px solid #dfe6e9; margin: 20px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    © 2024 Cafe Manager. Все права защищены.
                </p>
            </div>
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
        print(f"✅ Письмо с кодом {code} отправлено на {email}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки email: {e}")
        return False
