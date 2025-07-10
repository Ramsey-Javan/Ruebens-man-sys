from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db
from dotenv import load_dotenv
import os
from flask import render_template

# Load environment variables
load_dotenv()

# Import blueprints (routes)
from .route import main_bp, route_bp

# Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'route_bp.login'  # MUST match the blueprint where login route lives

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('SECRET_KEY')

    print("Loaded DATABASE_URL:", app.config['SQLALCHEMY_DATABASE_URI'])

    # Register error handler
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

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(route_bp)

    return app
