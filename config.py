import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cafe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 🔥 НАСТРОЙКИ ПОЧТЫ (Gmail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@gmail.com'  # 🔥 ТВОЙ Gmail
    MAIL_PASSWORD = 'your-app-password'      # 🔥 Пароль приложения (НЕ обычный пароль!)
    MAIL_DEFAULT_SENDER = 'your-email@gmail.com'
    
    # Для отладки (письма в консоль)
    # MAIL_SUPPRESS_SEND = False
