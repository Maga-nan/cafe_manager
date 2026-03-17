import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cafe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 🔥 НАСТРОЙКИ ПОЧТЫ (Gmail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'pavelpogreban22@gmail.com'  # Твой Gmail
    MAIL_PASSWORD = 'nulo lbnt fkol gvdi'        # Твой пароль приложения
    MAIL_DEFAULT_SENDER = 'pavelpogreban22@gmail.com'
