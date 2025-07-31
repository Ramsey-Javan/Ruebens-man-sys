from website import db, create_app
from website.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin_user = User(username="admin", password_hash=generate_password_hash("adminpass"), role="admin")
    teacher_user = User(username="teacher", password_hash=generate_password_hash("teacherpass"), role="teacher")
    parent_user = User(username="parent", password_hash=generate_password_hash("parentpass"), role="parent")

    db.session.add_all([admin_user, teacher_user, parent_user])
    db.session.commit()

    print("Users created successfully.")
