from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from collections import defaultdict
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from .forms import AddStudentForm, ClassSelectForm, PublicPerformanceForm
from website.services import auto_enroll_subjects
from website.forms import LoginForm

from website.models import (
    User, Student, Staff, Event, Spotlight, Grade10News,
    Grade, Classroom
)
from website.extensions import db


# Blueprints
main_bp = Blueprint('main_bp', __name__)
route_bp = Blueprint('route_bp', __name__)
public_bp = Blueprint('public_bp', __name__)

# ---------------------- Route to Home ----------------------
#Public Home Page
@public_bp.route('/welcome')
def public_home():
    school_info = {
        'name': 'St. Rueben School',
        'location': 'Kisii, Kenya',
        'student_count': 1200,
        'staff_count': 50,
        'mission': 'To provide quality education and holistic development.',
        'vision': 'To be a leading institution in academic excellence and character development.',
        'introduction': 'Welcome to St. Rueben School, where we nurture future leaders through quality education and character development.',
    }
    return render_template('public_home.html', info=school_info)
# Home (requires login)
@main_bp.route('/')
def home():
    from .models import Spotlight, Event
    if current_user.is_authenticated:
        Spotlight = Spotlight.query.order_by(Spotlight.posted_on.desc()).limit(5).all()
        events = Event.query.order_by(Event.date.desc()).limit(5).all()
        return render_template('index.html', spotlight=Spotlight, events=events)
    else:
        school_info = {
            'name': 'St. Rueben School',
            'location': 'Kisii, Kenya',
            'student_count': 1200,  
            'staff_count': 50,
            'mission': 'To provide quality education and holistic development.',
            'vision': 'To be a leading institution in academic excellence and character development.',
            'introduction': 'Welcome to St. Rueben School, where we nurture future leaders through quality education and character development.',
        }
        return render_template('public_home.html', info=school_info)
# ---------------------- Student Management ----------------------

# View all students + search + class filter + pagination
@route_bp.route('/students')
@login_required
def view_students():
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))
    from .forms import StudentSearchForm
    form = StudentSearchForm()

    search = request.args.get('search', '').strip()
    selected_class = request.args.get('class', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Start the query, join with Classroom
    query = db.session.query(Student).join(Classroom).options(db.joinedload(Student.classroom))

    # Apply search filter
    if search:
        query = query.filter(
            or_(
                Student.full_name.ilike(f'%{search}%'),
                Student.admission_number.ilike(f'%{search}%'),
                Classroom.class_name.ilike(f'%{search}%')
            )
        )

    # Apply class filter
    if selected_class:
        query = query.filter(Classroom.class_name == selected_class)

    pagination = query.order_by(Classroom.class_name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    students_paginated = pagination.items

    # Group students by class name
    grouped_students = defaultdict(list)
    for student in students_paginated:
        grouped_students[student.classroom.class_name].append(student)

    # Get distinct list of class names for the filter dropdown
    all_classes = (
        db.session.query(Classroom.class_name)
        .join(Student, Student.class_id == Classroom.id)
        .distinct()
        .all()
    )

    return render_template(
        'students.html',
        form=form,
        grouped_students=grouped_students,
        search=search,
        selected_class=selected_class,
        class_list=[cls[0] for cls in all_classes],
        pagination=pagination
    )


# Add student (GET shows form, POST submits it)
@route_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    from .forms import AddStudentForm
    from website.services import auto_enroll_subjects

    form = AddStudentForm()
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        admission_number = request.form.get('admission_number')
        UPI_number = request.form.get('upi_number')
        assesment_number = request.form.get('assessment_number')
        dob = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        class_id = request.form.get('class_id')
        parent_contact = request.form.get('parent_contact')

        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
            return redirect(url_for('route_bp.add_student'))

        new_student = Student(
            full_name=full_name,
            admission_number=admission_number,
            UPI_number=UPI_number,
            assesment_number=assesment_number,
            date_of_birth=dob,
            gender=gender,
            class_id=class_id,
            parent_contact=parent_contact
        )

        try:
            db.session.add(new_student)
            db.session.commit()

            auto_enroll_subjects(new_student)

            flash("Student added successfully!", "success")
            return redirect(url_for('route_bp.view_students'))

        except IntegrityError:
            db.session.rollback()
            flash("Admission number already exists. Please use a unique one.", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Unexpected error: {str(e)}", "error")

        return redirect(url_for('route_bp.add_student'))

    classrooms = Classroom.query.order_by(Classroom.class_name).all()
    return render_template('add_student.html', classrooms=classrooms, form=form)


# Edit student
@route_bp.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    from .forms import EditStudentForm
    form = EditStudentForm()
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    student = Student.query.get_or_404(student_id)
    classrooms = Classroom.query.order_by(Classroom.class_name.asc()).all()  #  Important

    if request.method == 'POST':
        student.full_name = request.form.get('full_name')
        student.admission_number = request.form.get('admission_number')
        student.UPI_number = request.form.get('upi_number')
        student.assessment_number = request.form.get('assessment_number')  #  Fixed typo

        try:
            student.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
            return redirect(url_for('route_bp.edit_student', student_id=student_id))

        student.gender = request.form.get('gender')

        # Assign class_id not class_name
        class_id = request.form.get('class_id')
        student.class_id = int(class_id) if class_id else None

        student.parent_contact = request.form.get('parent_contact')

        try:
            db.session.commit()
            flash("Student updated successfully!", "success")
            return redirect(url_for('route_bp.view_students'))
        except Exception as e:
            flash(f"Error updating student: {str(e)}", "error")

    return render_template('edit_student.html', student=student, classrooms=classrooms,form=form)  #Pass classrooms

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
    from website.forms import StaffSearchForm
    staff_list = Staff.query.all()
    form = StaffSearchForm()
    if current_user.role not in ['admin']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    staff_list = Staff.query.all()
    return render_template('staff.html', staff_list=staff_list,form=form)

@route_bp.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    from .forms import AddStaffForm
    staff_list = Staff.query.all
    form = AddStaffForm()
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

    return render_template('add_staff.html', form=form)

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
    form = LoginForm()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main_bp.home'))  # 🔁 One unified home
        else:
            flash('Invalid credentials. Try again.', 'error')

    return render_template('login.html',form=form)

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
    from website.forms import EventForm
    form = EventForm()

    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))


    if form.validate_on_submit():
        new_event = Event(
            title=form.title.data,
            date=form.date.data,
            location=form.location.data,
            description=form.description.data
        )
        db.session.add(new_event)
        db.session.commit()
        flash("Event added.", "success")
        return redirect(url_for('route_bp.view_events'))

    return render_template('add_event.html', form=form)

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
    from .forms import SpotlightForm
    form = SpotlightForm()
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

    return render_template('add_spotlight.html', form=form)

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
    from .forms import Grade10NewsForm
    form = Grade10NewsForm()
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
    return render_template('add_grade10news.html', form=form)

# Route to edit Grade 10 news
@route_bp.route('/grade10news/edit/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_grade10news(news_id):
    from .forms import Grade10NewsForm
    form = Grade10NewsForm()
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

    return render_template('edit_grade10news.html', news=news, form=form)

# Route to delete Grade 10 news

# ---------------------- Performance and Grade  ----------------------
# Add grade
@route_bp.route('/grades/add', methods=['GET', 'POST'])
@login_required
def add_grade():
    from .forms import AddGradeForm
    form = AddGradeForm()
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
    return render_template('add_grade.html', students=students, form=form)
# ---------------------- Bulk Grade Entry ----------------------
# Bulk Grade Entry
@route_bp.route('/grades/bulk', methods=['GET', 'POST'])
@route_bp.route('/grades/bulk/<int:class_id>', methods=['GET', 'POST'])
@login_required
def add_grades_bulk(class_id=None):
    from .forms import BulkGradeForm
    form = BulkGradeForm()
    if request.method == 'POST' and class_id is None:
        # First step: selecting the class
        class_id = request.form.get('class_id')
        return redirect(url_for('route_bp.add_grades_bulk', class_id=class_id))

    if class_id is None:
        # Step 1: show class selection form
        classes = Classroom.query.all()
        return render_template('select_class_for_grading.html', classes=classes)

    # Step 2: Show grading form or process submitted grades
    classroom = Classroom.query.get_or_404(class_id)
    students = Student.query.filter_by(class_id=class_id).all()
    current_year = datetime.now().year

    if request.method == 'POST':
        # ✅ FIX 1: Define subject, term, and year before using them
        subject = request.form.get('subject')
        term = request.form.get('term')
        year = request.form.get('year')

        # ✅ FIX 2: Validate them (optional but recommended)
        if not subject or not term or not year:
            flash("Subject, term, and year are required.", "danger")
            return redirect(url_for('route_bp.add_grades_bulk', class_id=class_id))

        added = 0
        for student in students:
            score = request.form.get(f'score_{student.id}')
            if score:
                try:
                    score = float(score)
                    new_grade = Grade(
                        student_id=student.id,
                        subject=subject,
                        score=score,
                        term=term,
                        year=year
                    )
                    db.session.add(new_grade)
                    added += 1
                except ValueError:
                    flash(f"Invalid score for {student.full_name}", "warning")

        db.session.commit()
        flash(f"{added} grades added successfully!", "success")
        return redirect(url_for('route_bp.view_grades'))

    return render_template(
        'bulk_grading_form.html',
        classroom=classroom,
        students=students,
        current_year=current_year,
        form=form
    )

# Edit grade
@route_bp.route('/grades/edit/<int:grade_id>', methods=['GET', 'POST'])
@login_required
def edit_grade(grade_id):   
    from .forms import EditGradeForm
    form = EditGradeForm()
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
    return render_template('edit_grade.html', grade=grade, students=students, form=form)

# View grades with filters
@route_bp.route('/grades', methods=['GET'])
@login_required
def view_grades():
    from website.forms import GradeSearchForm
    form = GradeSearchForm()
    
    if current_user.role not in ['admin', 'teacher']:
        flash("Access denied.", "error")
        return redirect(url_for('main_bp.home'))

    year_filter = request.args.get('year')
    term_filter = request.args.get('term')
    class_filter = request.args.get('class_name')

    query = db.session.query(Grade).join(Student).join(Classroom)

    if year_filter:
        query = query.filter(Grade.year == year_filter)
    if term_filter:
        query = query.filter(Grade.term == term_filter)
    if class_filter:
        query = query.filter(Classroom.class_name == class_filter)

    grades = query.order_by(Grade.year.desc(), Grade.term).all()

    years = sorted({g.year for g in Grade.query.all()}, reverse=True)
    terms = sorted({g.term for g in Grade.query.all()})
    class_names = sorted({s.classroom.class_name for s in Student.query.all() if s.classroom})

    return render_template(
        'grades.html',
        grades=grades,
        years=years,
        terms=terms,
        class_names=class_names,
        form = form
    )

# ---------------------- Parents and Public Routes ----------------------   
# ------------------ Parents Grade Access ------------------
@route_bp.route('/view-performance', methods=['GET', 'POST'])
def public_view_performance():
    form = PublicPerformanceForm()
    
    #  Block logged-in admins/teachers FIRST
    if current_user.is_authenticated and current_user.role in ['admin', 'teacher']:
        flash("You are already logged in. Please log out to view performance as a parent.", "info")
        return redirect(url_for('main_bp.home'))

    if form.validate_on_submit():
        full_name = form.name.data.strip()
        admission_number = form.admission_number.data.strip()

        student = Student.query.filter(
            db.func.lower(Student.full_name) == full_name.lower(),
            Student.admission_number == admission_number
        ).first()

        if not student:
            flash("No matching student found. Please check the name and admission number.", "error")
            return redirect(url_for('route_bp.public_view_performance'))

        grades = Grade.query.filter_by(student_id=student.id).order_by(Grade.year.desc(), Grade.term).all()

        if not grades:
            flash("No grades found for this student.", "info")
            return redirect(url_for('route_bp.public_view_performance'))

        # Group grades by year and term
        grouped_grades = defaultdict(lambda: defaultdict(list))
        for grade in grades:
            grouped_grades[grade.year][grade.term].append(grade)

        return render_template(
            'public_grades.html',
            student=student,
            grouped_grades=grouped_grades
        )

    # Always return form at the end
    return render_template(
        'view_performance.html',
        student=None,
        grouped_grades=None,
        form=form
    )


#Parents View of Grades 
@route_bp.route('/grades/view', methods=['GET', 'POST'])
@login_required
def view_student_grades():
    if current_user.role != 'parent':
        abort(403)

    grades = []
    if request.method == 'POST':
        admission_no = request.form['admission_no']
        student = Student.query.filter_by(admission_no=admission_no).first()
        if student:
            grades = Grade.query.filter_by(student_id=student.id).all()
        else:
            flash("Student not found", "danger")

    return render_template('view_student_grades.html', grades=grades)


# ---------------------- Error Handlers ----------------------
