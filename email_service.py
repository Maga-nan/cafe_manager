from models import db, VerificationCode, Email
from datetime import datetime
import random
import string

def generate_code(length=6):
    """Генерирует случайный код из цифр"""
    return ''.join(random.choices(string.digits, k=length))

def save_verification_code(email, code, username, password_hash, role):
    """
    Сохраняет код подтверждения в базу данных.
    Код будет виден в окне /admin/codes
    """
    try:
        # Удаляем старые неиспользованные коды для этого email
        old_codes = VerificationCode.query.filter_by(email=email, is_used=False).all()
        for old in old_codes:
            db.session.delete(old)
        
        # Сохраняем новый код
        verification = VerificationCode(
            email=email,
            code=code,
            username=username,
            password_hash=password_hash,
            role=role,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(verification)
        
        # Также сохраняем как "письмо" для отображения в интерфейсе
        email_record = Email(
            recipient_email=email,
            subject='☕ Код подтверждения',
            body=f'<div style="font-size:32px;font-weight:bold;text-align:center">{code}</div>',
            sent_at=datetime.utcnow()
        )
        db.session.add(email_record)
        
        db.session.commit()
        print(f"✅ Код {code} сохранён для {email}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.session.rollback()
        return False
