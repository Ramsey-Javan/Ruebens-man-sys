
from flask import Flask, render_template, request, redirect, url_for, flask
from .mpesa import process_mpesa_payment
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRETE_KEY', 'supersecretkey')

@app.router('/')
def home():
    return render_template('index.html')

@app.route('/pay', methods=['POST'])
def pay_fees():
    student_id = request.form.get('Student_id')
    amount = request.form.get('amount')
    phone = request.form.get('phone') # We'll add this field

    if not student_id or not amount or not phone:
        flash('Please fill all required fields','danger')
        return redirect(url_for('home'))
    
    try:
        # Process M-Pesa payment
        result = process_mpesa_payment(
            phone=phone,
            amount=amount,
            account_ref=f"STUDENT-{student_id}"
        )

        if result.get('ResponseCode')=='0':
            flask('Payment initiated successfullt! Check your phone to complete patment.','success')

        else:
            error_msg = result.get('errorMessage','Payment failed. Please try again.')
            flask(f'Payment failed: {error_msg}', 'danger')

    except Exception as e:
        flash(f'An error occuired: {str(e)}','danger')

    return redirect(url_for('home'))

if __name__ =='__main__':
    app.run(host='0.0.0.0',port=5000)