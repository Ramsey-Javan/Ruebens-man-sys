from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from dotenv import load_dotenv
import os

from .models import db, Classroom, User  # Include both Classroom and User
from .route import main_bp, route_bp, public_bp  # Register all blueprints


# Load environment variables
load_dotenv()

csrf = CSRFProtect()

# Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'route_bp.login'  # Where your login route is

# Register the user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['WTF_CSRF_ENABLED'] = True # Enable CSRF protection (False by default)

    print(f"Loaded DATABASE_URL: {os.getenv('DATABASE_URL')}")

    # Register blueprints (order matters: public first for root route)

    app.register_blueprint(route_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(public_bp, url_prefix='/welcome')

    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    csrf.init_app(app)

    # CSRF token injection for templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf())
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    return app
