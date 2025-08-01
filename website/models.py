from website.extensions import db, csrf, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from website.extensions import db
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
#db = SQLAlchemy()
#from website.extensions import db

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

    #  Proper relationship to Grade
    grades = db.relationship('Grade', back_populates='student', lazy=True)
    classroom = db.relationship('Classroom', back_populates='students')
    performances = db.relationship('Performance', back_populates='student', cascade="all, delete-orphan")


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
    
# GradeLevel = PP1, Grade 1, Grade 2, etc.
class GradeLevel(db.Model):
    __tablename__ = 'grade_levels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    subjects = db.relationship('Subject', backref='grade_level', lazy=True)

    def __repr__(self):
        return f"<GradeLevel {self.name}>"


# Subject (linked to grade)
class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade_level_id = db.Column(db.Integer, db.ForeignKey('grade_levels.id'), nullable=False)

    def __repr__(self):
        return f"<Subject {self.name} for Grade {self.grade_level.name}>"


# Link Student to Subjects (after auto-enrollment)
class StudentSubject(db.Model):
    __tablename__ = 'student_subjects'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    def __repr__(self):
        return f"<StudentSubject Student={self.student_id} Subject={self.subject_id}>"

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
    __tablename__ = 'grades'
    __table_args__ = (
    db.Index('idx_grade_student', 'student_id'),
    db.Index('idx_grade_year_term', 'year', 'term'),
    db.Index('idx_grade_strand', 'strand'),
    db.Index('idx_grade_learning_area', 'learning_area'),
)
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    learning_area = db.Column(db.String(100), nullable=False)  
    strand = db.Column(db.String(100)) 
    sub_strand = db.Column(db.String(100))  
    cbc_level = db.Column(db.Integer, nullable=False)  
    term = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False, default=lambda: datetime.now().year)
    teacher_comment = db.Column(db.Text)  
    posted_on = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', back_populates='grades')

    def __repr__(self):
        return f"<Grade {self.strand} - Level {self.cbc_level} for {self.student.full_name}>"
class Performance(db.Model):
    __tablename__ = 'performances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    term = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False, default=lambda: datetime.now().year)
    average_score = db.Column(db.Float, nullable=False)
    rank = db.Column(db.Integer, nullable=True) 
    summary = db.Column(db.Text, nullable=True)
    
    student = db.relationship('Student', back_populates='performances')

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
