from flask import Flask
from flask_login import LoginManager
from .models import db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import blueprints only (no User!)
from .route import main_bp, route_bp

login_manager = LoginManager()
login_manager.login_view = 'route_bp.login'

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('SECRET_KEY')

    print("Loaded DATABASE_URL:\", app.config['SQLALCHEMY_DATABASE_URI")

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(route_bp)

    return app
