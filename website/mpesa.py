
import requests
import os 

def process_mpesa_payment(phone, amount, account_ref):
    """Process M-Pesa payment using Safaricom API"""
    api_key = os.getenv('MPESA_API_KEY', 'test_api_key')
    # Sandbox URL - replace with production in real deployment 
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Countent_Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": "174379",
        "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwMjI4MTEyNTI3",
        "Timestamp": "20240228112527",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": "174379",
        "PhoneNumber": phone,
        "CallBackURL": "https://yourdomain.com/callback",
        "AccountReference": account_ref,
        "TransactionDesc": "Payment for services"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
