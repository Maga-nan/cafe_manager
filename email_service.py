from models import db, Email
from datetime import datetime
import random
import string

def generate_code(length=6):
    """Генерирует случайный код из цифр"""
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email, code, username):
    """
    Сохраняет код подтверждения в базу данных (внутренняя почта)
    НЕ отправляет на реальный email
    """
    try:
        # Создаём HTML версию письма с кодом
        html_body = f'''
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
                    💡 Откройте <strong>Почту Cafe</strong> (порт 5001), 
                    чтобы посмотреть этот код.
                </p>
                <hr style="border: none; border-top: 1px solid #dfe6e9; margin: 20px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    © 2024 Cafe Manager. Все права защищены.
                </p>
            </div>
        </body>
        </html>
        '''
        
        # Сохраняем письмо в базу данных (внутренняя почта)
        email_record = Email(
            recipient_email=email,
            subject='☕ Подтверждение регистрации - Cafe Manager',
            body=html_body,
            sent_at=datetime.utcnow()
        )
        db.session.add(email_record)
        db.session.commit()
        
        print(f"✅ Код {code} сохранён в почте для {email}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сохранения email: {e}")
        db.session.rollback()
        return False
