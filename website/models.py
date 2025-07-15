from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    admission_number = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    parent_contact = db.Column(db.String(15), nullable=False)
    UPI_number = db.Column(db.String(20), unique=True, nullable=False)
    assesment_number = db.Column(db.String(20), unique=True, nullable=False)

    classroom = db.relationship('Classroom', back_populates='students', lazy=True)
    grades = db.relationship('Grade', back_populates='student', lazy=True)

    def __repr__(self):
        return f"<Student {self.full_name} - {self.admission_number}>"

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True) # null based from false to true 

    students = db.relationship('Student', back_populates='classroom', lazy=True)

    def __repr__(self):
        return f"<Classroom {self.class_name}>"

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Staff {self.full_name} - {self.role}>"


# Grade and Performance models
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    term = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False, default=lambda: datetime.now().year)
    posted_on = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return f"<Grade {self.subject} - {self.score} for Student ID {self.student_id}>"

# performance model
class Performance(db.Model):
    __tablename__ = 'performances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    term = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False, default=lambda: datetime.now().year)
    average_score = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Performance for Student ID {self.student_id} - {self.term} {self.year}: {self.average_score}>"

# Form for searching student performance
class PerformanceSearchForm(FlaskForm): 
    name = StringField("Student Name", validators=[DataRequired()])
    admission_number = StringField("Admission Number", validators=[DataRequired()])
    submit = SubmitField("View Performance")

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Event {self.title} on {self.date}>"

class Spotlight(db.Model):
    __tablename__ = 'spotlights'
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Spotlight {self.headline}>"

class Grade10News(db.Model):
    __tablename__ = 'grade10news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Grade10News {self.title}>"

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
<<<<<<< HEAD
    
=======
>>>>>>> b216992 (Fix Grade model, clean migrations, working display)
