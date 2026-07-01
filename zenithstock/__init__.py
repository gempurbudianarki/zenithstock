import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-key-for-dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///zenithstock.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Cookie security settings
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'

    # Bind extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu untuk mengakses halaman ini.'
    login_manager.login_message_category = 'warning'

    # Import blueprints inside factory to avoid circular imports
    from zenithstock.routes.auth import auth_bp
    from zenithstock.routes.dashboard import dashboard_bp
    from zenithstock.routes.suppliers import suppliers_bp
    from zenithstock.routes.movements import movements_bp
    from zenithstock.routes.analytics import analytics_bp
    from zenithstock.routes.audit import audit_bp
    from zenithstock.routes.users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(movements_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(users_bp)

    # Set user loader
    from zenithstock.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error handlers
    from flask import render_template as rt

    @app.errorhandler(403)
    def forbidden(e):
        return rt('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return rt('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return rt('errors/500.html'), 500

    # Create tables and seed data automatically in development
    with app.app_context():
        db.create_all()
        seed_data()

    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        from zenithstock.models import Product
        if current_user.is_authenticated:
            critical_products = Product.query.filter(Product.stok <= Product.min_stok).all()
            return {
                'global_critical_products': critical_products,
                'global_critical_count': len(critical_products)
            }
        return {
            'global_critical_products': [],
            'global_critical_count': 0
        }

    return app


def seed_data():
    from zenithstock.models import User, Supplier
    
    # Check if we have any users
    if User.query.first() is None:
        # Create Admin
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create Staff
        staff = User(username='staff', role='staff')
        staff.set_password('staff123')
        db.session.add(staff)
        
        db.session.commit()
        print("[SEED] Default Users (admin/admin123 dan staff/staff123) berhasil dibuat.")
        
    # Check if we have any suppliers
    if Supplier.query.first() is None:
        s1 = Supplier(nama="PT Global Elektronika", kontak="Hendra", telepon="021-889900", alamat="Kawasan Industri Jababeka, Bekasi")
        s2 = Supplier(nama="CV Berkah Stationary", kontak="Siti Aminah", telepon="0812-3456-789", alamat="Jl. Margonda Raya No. 45, Depok")
        db.session.add(s1)
        db.session.add(s2)
        db.session.commit()
        print("[SEED] Default Suppliers berhasil dibuat.")
