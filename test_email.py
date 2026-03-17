# test_email.py
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pavelpogreban22@gmail.com'
app.config['MAIL_PASSWORD'] = 'nulo lbnt fkol gvdi'
app.config['MAIL_DEFAULT_SENDER'] = 'pavelpogreban22@gmail.com'

mail = Mail(app)

with app.app_context():
    try:
        msg = Message(
            subject='🧪 ТЕСТОВОЕ ПИСЬМО',
            recipients=['pavelpogreban22@gmail.com']
        )
        msg.body = 'Если ты это читаешь — значит отправка работает! ✅'
        mail.send(msg)
        print("✅ Письмо отправлено!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
