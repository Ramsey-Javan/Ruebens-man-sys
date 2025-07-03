import os
import base64
import requests
import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def get_access_token():
    """Fetches access token from Safaricom Daraja API."""
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')

    if not consumer_key or not consumer_secret:
        raise Exception("Missing MPESA_CONSUMER_KEY or MPESA_CONSUMER_SECRET")

    credentials = f"{consumer_key}:{consumer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to obtain access token: {response.text}")


def process_mpesa_payment(phone, amount, account_ref):
    """Initiates STK Push request to Safaricom Daraja API."""
    access_token = get_access_token()

    business_short_code = "174379"
    passkey = os.getenv('MPESA_PASSKEY')

    if not passkey:
        raise Exception("Missing MPESA_PASSKEY")

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = business_short_code + passkey + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": business_short_code,
        "PhoneNumber": phone,
        "CallBackURL": "https://webhook.site/your-custom-url",  # Replace with your real URL
        "AccountReference": account_ref,
        "TransactionDesc": "School Fees Payment"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
