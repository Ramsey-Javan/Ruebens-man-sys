
from . import app
from flask import render_template, request, jsonify
from .mpesa import process_mpesa_payment
from .backend import database_operation

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mpesa-pay', methods=['POST'])
def mpesa_payment():
    data = request.get_json()
    result = process_mpesa_payment(
        data['phone'],
        data['amount'],
        data['account']
    )
    return jsonify(result)

@app.route('/backend', methods=['POST'])
def backend_process():
    data = request.get_json()
    result = database_operation(data)
    return jsonify({"status": "success", "data": result})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)