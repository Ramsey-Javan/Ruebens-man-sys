# app.py
from website import create_app
from website.models import db, User
from flask_login import LoginManager
from flask import render_template
import logging

logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = create_app()

# Flask-Login config
login_manager = LoginManager()
login_manager.login_view = 'route_bp.login'  # ✅ FIXED from 'main_bp.login'
login_manager.init_app(app)

# Load user from session using user ID (integer primary key)
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None  # Avoid crash if invalid session

# Handle Internal Server Error with custom 500.html
@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

# Create DB and default users
with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('adminpass')
        db.session.add(admin)

    if not User.query.filter_by(username='teacher').first():
        teacher = User(username='teacher', role='teacher')
        teacher.set_password('teacherpass')
        db.session.add(teacher)

    if not User.query.filter_by(username='parent').first():
        parent = User(username='parent', role='parent')
        parent.set_password('parentpass')
        db.session.add(parent)

    db.session.commit()

# Start app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
