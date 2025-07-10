from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from website.models import User, Student
from werkzeug.security import check_password_hash
from datetime import datetime
from collections import defaultdict
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from website import db
from website.models import Staff
from flask_login import login_required
from website.models import Event
from website.models import Spotlight, Grade10News
from website.models import db
from website.models import Grade


# Blueprints
main_bp = Blueprint('main_bp', __name__)
route_bp = Blueprint('route_bp', __name__)

# Home (requires login)
@main_bp.route('/')
@login_required
def home():
    return render_template('index.html')

# ---------------------- Student Management ----------------------

# View all students + search support
@route_bp.route('/students')
@login_required
def view_students():
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    search = request.args.get('search', '').strip()
    selected_class = request.args.get('class', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Student.query

    if search:
        query = query.filter(
            or_(
                Student.full_name.ilike(f'%{search}%'),
                Student.admission_number.ilike(f'%{search}%'),
                Student.class_name.ilike(f'%{search}%')
            )
        )

    if selected_class:
        query = query.filter_by(class_name=selected_class)

    pagination = query.order_by(Student.class_name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    students_paginated = pagination.items

    grouped_students = defaultdict(list)
    for student in students_paginated:
        grouped_students[student.class_name].append(student)

    all_classes = [c[0] for c in Student.query.with_entities(Student.class_name).distinct()]

    return render_template(
        'students.html',
        grouped_students=grouped_students,
        search=search,
        selected_class=selected_class,
        class_list=all_classes,
        pagination=pagination
    )

# Add student (GET shows form, POST submits it)
@route_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        admission_number = request.form.get('admission_number')
        dob = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        class_name = request.form.get('class_name')
        parent_contact = request.form.get('parent_contact')

        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
            return redirect(url_for('route_bp.add_student'))

        new_student = Student(
            full_name=full_name,
            admission_number=admission_number,
            date_of_birth=dob,
            gender=gender,
            class_name=class_name,
            parent_contact=parent_contact
        )

        try:
            db.session.add(new_student)
            db.session.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for('route_bp.view_students'))

        except IntegrityError:
            db.session.rollback()
            flash("Admission number already exists. Please use a unique one.", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Unexpected error: {str(e)}", "error")

        return redirect(url_for('route_bp.add_student'))

    return render_template('add_student.html')

# Edit student
@route_bp.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.full_name = request.form.get('full_name')
        student.admission_number = request.form.get('admission_number')
        try:
            student.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
            return redirect(url_for('route_bp.edit_student', student_id=student_id))
        student.gender = request.form.get('gender')
        student.class_name = request.form.get('class_name')
        student.parent_contact = request.form.get('parent_contact')

        try:
            from website.models import db
            db.session.commit()
            flash("Student updated successfully!", "success")
            return redirect(url_for('route_bp.view_students'))
        except Exception as e:
            flash(f"Error updating student: {str(e)}", "error")

    return render_template('edit_student.html', student=student)

# Delete student
@route_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    student = Student.query.get_or_404(student_id)
    try:
        from website.models import db
        db.session.delete(student)
        db.session.commit()
        flash("Student deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting student: {str(e)}", "error")

    return redirect(url_for('route_bp.view_students'))

# ---------------------- Staff Management ----------------------
@route_bp.route('/staff')
@login_required
def view_staff():
    if current_user.role not in ['admin']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    staff_list = Staff.query.all()
    return render_template('staff.html', staff_list=staff_list)

@route_bp.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    if current_user.role not in ['admin']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        staff_id = request.form.get('staff_id')
        role = request.form.get('role')
        contact = request.form.get('contact')
        email = request.form.get('email')

        # Check if any required field is empty
        if not all([full_name, staff_id, role, contact, email]):
            flash("All fields are required. Please fill in all details.", "error")
            return render_template('add_staff.html')

        # Check if staff ID or email already exists
        existing_staff = Staff.query.filter(
            (Staff.staff_id == staff_id) | (Staff.email == email)
        ).first()
        if existing_staff:
            flash("Staff ID or email already exists. Please use unique values.", "error")
            return render_template('add_staff.html')

        new_staff = Staff(
            full_name=full_name,
            staff_id=staff_id,
            role=role,
            contact=contact,
            email=email
        )

        try:
            db.session.add(new_staff)
            db.session.commit()
            flash("Staff member added successfully!", "success")
            return redirect(url_for('route_bp.view_staff'))
        except Exception as e:
            db.session.rollback()
            flash(f"Unexpected error: {str(e)}", "error")

    return render_template('add_staff.html')

@route_bp.route('/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
@login_required
def edit_staff(staff_id):
    if current_user.role not in ['admin']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    staff = Staff.query.get_or_404(staff_id)

    if request.method == 'POST':
        staff.full_name = request.form.get('full_name')
        staff.staff_id = request.form.get('staff_id')
        staff.role = request.form.get('role')
        staff.contact = request.form.get('contact')
        staff.email = request.form.get('email')

        try:
            db.session.commit()
            flash("Staff member updated successfully!", "success")
            return redirect(url_for('route_bp.view_staff'))
        except Exception as e:
            flash(f"Error updating staff member: {str(e)}", "error")

    return render_template('edit_staff.html', staff=staff)

@route_bp.route('/staff/delete/<int:staff_id>', methods=['POST'])
@login_required
def delete_staff(staff_id):
    if current_user.role not in ['admin']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    staff = Staff.query.get_or_404(staff_id)
    try:
        db.session.delete(staff)
        db.session.commit()
        flash("Staff member deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting staff member: {str(e)}", "error")

    return redirect(url_for('route_bp.view_staff'))


# ---------------------- Auth Routes ----------------------

# Login
@route_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main_bp.home'))
        else:
            flash('Invalid credentials. Try again.', 'error')

    return render_template('login.html')

# Logout
@route_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('route_bp.login'))

# ---------------------- M-Pesa Placeholder ----------------------

@main_bp.route('/pay_fees', methods=['POST'])
@login_required
def pay_fees():
    student_id = request.form.get('Student_id')
    phone = request.form.get('phone')
    amount = request.form.get('amount')

    print(f"Received payment from student {student_id}, phone {phone}, amount KES {amount}")
    flash("Payment initiated successfully.", "success")

    return redirect(url_for('main_bp.home'))

# ---------------------- Live Events ----------------------
@route_bp.route('/events')
@login_required
def view_events():
    events = Event.query.order_by(Event.date).all()
    return render_template('events.html', events=events)

@route_bp.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        location = request.form['location']
        description = request.form['description']
        new_event = Event(title=title, date=date, location=location, description=description)
        db.session.add(new_event)
        db.session.commit()
        flash("Event added.", "success")
        return redirect(url_for('route_bp.view_events'))

    return render_template('add_event.html')

# Spotlight 
@route_bp.route('/spotlight')
@login_required
def view_spotlight():
    if current_user.role not in ['admin', 'teacher', 'parent']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    spotlights = Spotlight.query.order_by(Spotlight.posted_on.desc()).all()
    return render_template('spotlight.html', spotlights=spotlights)
    
# Add spotlight
@route_bp.route('/spotlight/add', methods=['GET', 'POST'])
@login_required
def add_spotlight():
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    if request.method == 'POST':
        headline = request.form.get('headline')
        body = request.form.get('body')

        new_spotlight = Spotlight(headline=headline, body=body)

        try:
            db.session.add(new_spotlight)
            db.session.commit()
            flash("Spotlight posted successfully!", "success")
            return redirect(url_for('route_bp.view_spotlight'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")

    return render_template('add_spotlight.html')

# ---------------------- Grade 10 News ----------------------
# Route to view Grade 10 news
@route_bp.route('/grade10news')
@login_required
def view_grade10news():
    if current_user.role not in ['admin', 'teacher', 'parent']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    news_list = Grade10News.query.order_by(Grade10News.posted_on.desc()).all()
    return render_template('grade10news.html', news_list=news_list)

#Route to add Grade 10 news
@route_bp.route('/grade10news/add', methods=['GET', 'POST'])
@login_required
def add_grade10news():
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        news = Grade10News(title=title, content=content)
        db.session.add(news)
        db.session.commit()
        flash('Grade 10 News added.', 'success')
        return redirect(url_for('route_bp.view_grade10news'))
    return render_template('add_grade10news.html')

# Route to edit Grade 10 news
@route_bp.route('/grade10news/edit/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_grade10news(news_id):
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    news = Grade10News.query.get_or_404(news_id)

    if request.method == 'POST':
        news.title = request.form['title']
        news.content = request.form['content']
        db.session.commit()
        flash('Grade 10 News updated.', 'success')
        return redirect(url_for('route_bp.view_grade10news'))

    return render_template('edit_grade10news.html', news=news)

# Route to delete Grade 10 news

# ---------------------- Performance and Grade  ----------------------
# Add grade
@route_bp.route('/grades/add', methods=['GET', 'POST'])
@login_required
def add_grade():
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        score = request.form['score']
        term = request.form['term']

        grade = Grade(
            student_id=student_id,
            subject=subject,
            score=score,
            term=term
        )
        db.session.add(grade)
        db.session.commit()
        flash("Grade added successfully.", "success")
        return redirect(url_for('route_bp.view_grades'))

    students = Student.query.all()
    return render_template('add_grade.html', students=students)

# Edit grade
@route_bp.route('/grades/edit/<int:grade_id>', methods=['GET', 'POST'])
@login_required
def edit_grade(grade_id):   
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    grade = Grade.query.get_or_404(grade_id)

    if request.method == 'POST':
        grade.student_id = request.form['student_id']
        grade.subject = request.form['subject']
        grade.score = request.form['score']
        grade.term = request.form['term']
        db.session.commit()
        flash("Grade updated successfully.", "success")
        return redirect(url_for('route_bp.view_grades'))

    students = Student.query.all()
    return render_template('edit_grade.html', grade=grade, students=students)

# View grades with filters
@route_bp.route('/grades', methods=['GET'])
@login_required
def view_grades():
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    year_filter = request.args.get('year')
    term_filter = request.args.get('term')
    class_filter = request.args.get('class_name')

    query = Grade.query.join(Student)

    if year_filter:
        query = query.filter(Grade.year == year_filter)
    if term_filter:
        query = query.filter(Grade.term == term_filter)
    if class_filter:
        query = query.filter(Student.class_name == class_filter)

    grades = query.order_by(Grade.year.desc(), Grade.term).all()

    years = sorted({g.year for g in Grade.query.all()}, reverse=True)
    terms = sorted({g.term for g in Grade.query.all()})
    class_names = sorted({s.class_name for s in Student.query.all()})

    return render_template(
        'grades.html',
        grades=grades,
        years=years,
        terms=terms,
        class_names=class_names
    )
