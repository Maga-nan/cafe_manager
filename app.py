from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User
from routes.auth import auth_bp
from routes.orders import orders_bp
from routes.menu import menu_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(menu_bp, url_prefix='/menu')
    
    with app.app_context():
        db.create_all()
        create_default_user()
    
    return app

def create_default_user():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@cafe.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
