from website.models import User
from werkzeug.security import generate_password_hash
from website.extensions import db

def populate_users():
    default_users = [
        {
            "username": "admin",
            "password": "adminpass",
            "role": "admin"
        },
        {
            "username": "teacher",
            "password": "teacherpass",
            "role": "teacher"
        },
        {
            "username": "parent",
            "password": "parentpass",
            "role": "parent"
        }
    ]

    for user_data in default_users:
        existing_user = User.query.filter_by(username=user_data["username"]).first()
        if not existing_user:
            user = User(
                username=user_data["username"],
                password_hash=generate_password_hash(user_data["password"]),
                role=user_data["role"]
            )
            db.session.add(user)
            print(f"✅ Created user: {user_data['username']}")
        else:
            print(f"ℹ️ User {user_data['username']} already exists.")

    db.session.commit()
