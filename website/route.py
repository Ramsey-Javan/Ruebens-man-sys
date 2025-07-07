from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from website.models import User, Student
from werkzeug.security import check_password_hash
from datetime import datetime

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

    query = request.args.get('search', '').strip()
    if query:
        students = Student.query.filter(
            Student.full_name.ilike(f'%{query}%') |
            Student.admission_number.ilike(f'%{query}%') |
            Student.class_name.ilike(f'%{query}%')
        ).all()
    else:
        students = Student.query.all()
    return render_template('students.html', students=students, search=query)

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

        # Convert string to date
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
            from website.models import db
            db.session.add(new_student)
            db.session.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for('route_bp.view_students'))
        except Exception as e:
            flash(f"Error adding student: {str(e)}", "error")

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
