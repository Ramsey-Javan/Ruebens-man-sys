import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from dotenv import load_dotenv

# Local imports
from website.extensions import db, login_manager, csrf
from website.models import User
from website.route import main_bp, route_bp, public_bp
from website.services import auto_enroll_subjects
from website.populate_users import populate_users
from website.populate_classrooms import populate_classrooms


# Load environment variables
load_dotenv()

# Initialize extensions (defined once)
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'route_bp.login'


# Define user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # App configuration
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
        SECRET_KEY=os.getenv('SECRET_KEY'),
        WTF_CSRF_ENABLED=True,
    )

    print(f"[INIT] Loaded DATABASE_URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Register blueprints
    app.register_blueprint(public_bp, url_prefix='/welcome')  # Public first
    app.register_blueprint(main_bp)
    app.register_blueprint(route_bp)

    # Init extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    # Run population scripts 
    with app.app_context():
        db.create_all()  # Ensure database tables are created
        populate_users() # Populate default users
        populate_classrooms() # Populate default classrooms
        
    # Inject CSRF token in all templates
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

    return app