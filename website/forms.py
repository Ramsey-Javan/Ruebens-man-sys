from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FileField, IntegerField
from wtforms.fields import DateField, TimeField  # ✅ this is the key line
from wtforms.validators import DataRequired, Length, Optional

from website.models import Student



class ClassSelectForm(FlaskForm):
    class_id = SelectField('Choose Class', coerce=int)
    submit = SubmitField('Proceed')

# ---------------- LOGIN FORM ----------------
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# ---------------- ADD CLASS ----------------
class AddStudentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    admission_number = StringField('Admission Number', validators=[DataRequired()])
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Student')


# ---------------- EDIT STUDENT ----------------
class EditStudentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    admission_number = StringField('Admission Number', validators=[DataRequired()])
    class_id = SelectField('Classroom', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Update Student')


# ---------------- ADD STAFF ----------------
class AddStaffForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('teacher', 'Teacher'), ('parent', 'Parent')], validators=[DataRequired()])
    submit = SubmitField('Add Staff')


# ---------------- ADD GRADE ----------------
class AddGradeForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    score = IntegerField('Score', validators=[DataRequired()])
    term = StringField('Term', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    submit = SubmitField('Add Grade')


# ---------------- BULK GRADING ----------------
class BulkGradeForm(FlaskForm):
    class_id = SelectField('Classroom', coerce=int, validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    term = StringField('Term', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    submit = SubmitField('Submit Grades')


# ---------------- EDIT GRADE ----------------
class EditGradeForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    score = IntegerField('Score', validators=[DataRequired()])
    term = StringField('Term', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    submit = SubmitField('Update Grade')


# ---------------- EVENT FORM ----------------
class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    submit = SubmitField('Create Event')


# ---------------- SPOTLIGHT FORM ----------------
class SpotlightForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Upload Image (Optional)', validators=[Optional()])
    submit = SubmitField('Add Spotlight')


# ---------------- GRADE 10 NEWS FORM ----------------
class Grade10NewsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post News')


# --------------- PUBLIC GRADES ACCES  -------------
class PublicPerformanceForm(FlaskForm):
    name = StringField('Name ', validators=[DataRequired()])
    admission_number = StringField('Admission Number', validators=[DataRequired()])
    term = SelectField('Term', choices=[
        ('', 'Any'), ('1', 'Term 1'), ('2', 'Term 2'), ('3', 'Term 3')
    ], validators=[Optional()])
    year = StringField('Year', validators=[Optional()])
    subject = StringField('Subject', validators=[Optional()])
    submit = SubmitField('Search')

# ------------- STAFF SEARCH ----------
class StaffSearchForm(FlaskForm):
    search = StringField('Search Staff')
    submit = SubmitField('Search')

#----------- GRDAES SEARCH -----------
class GradeSearchForm(FlaskForm):
    admission_no = StringField('Admission Number', validators=[Optional()])
    student_class = StringField('Class', validators=[Optional()])
    submit = SubmitField('Search')

#------------ EVENTS FORM  -----------
class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired()])
    description = TextAreaField('Event Description', validators=[DataRequired()])
    date = DateField('Event Date', validators=[DataRequired()])
    time = TimeField('Event Time', validators=[DataRequired()])
    location = StringField('Event Location', validators=[DataRequired()])
    organizer = StringField('Event Organizer', validators=[DataRequired()])
    submit = SubmitField('Add Event')