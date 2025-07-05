from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from website.models import User
from werkzeug.security import check_password_hash

# Blueprints
main_bp = Blueprint('main_bp', __name__)
route_bp = Blueprint('route_bp', __name__)

# Home (requires login)
@main_bp.route('/')
@login_required
def home():
    return render_template('index.html')

# Add student page
@route_bp.route('/add_student')
@login_required
def add_student():
    return render_template('add_students.html')

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

# Pay fees
@main_bp.route('/pay_fees', methods=['POST'])
@login_required
def pay_fees():
    student_id = request.form.get('Student_id')
    phone = request.form.get('phone')
    amount = request.form.get('amount')

    # M-Pesa integration placeholder
    print(f"Received payment from student {student_id}, phone {phone}, amount KES {amount}")
    flash("Payment initiated successfully.", "success")

    return redirect(url_for('main_bp.home'))
