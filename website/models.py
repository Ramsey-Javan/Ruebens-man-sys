# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    admission_number = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    parent_contact = db.Column(db.String(15), nullable=False)

    grades = db.relationship('Grade', backref='student', lazy=True)

    def __repr__(self):
        return f"<Student {self.full_name} - {self.admission_number}>"

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f"<Staff {self.full_name} - {self.role}>"

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    term = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Grade {self.subject} - {self.marks} Marks>"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"
