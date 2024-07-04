from flask import Flask, request, jsonify, render_template
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

app = Flask(__name__)

# M-Pesa credentials
CONSUMER_KEY = '01'
CONSUMER_SECRET = '02'
BUSINESS_SHORT_CODE = '174379'
PASSKEY = '03'
CALLBACK_URL = '04'

def get_access_token(consumer_key, consumer_secret):
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = response.json().get('access_token')
    return access_token

def lipa_na_mpesa_online(amount, phone_number):
    access_token = get_access_token(CONSUMER_KEY, CONSUMER_SECRET)
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f'{BUSINESS_SHORT_CODE}{PASSKEY}{timestamp}'.encode()).decode('utf-8')

    payload = {
        "BusinessShortCode": BUSINESS_SHORT_CODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": BUSINESS_SHORT_CODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": '123456',
        "TransactionDesc": 'Payment for testing'
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pay', methods=['POST'])
def pay():
    amount = request.form['amount']
    phone_number = request.form['phone_number']
    response = lipa_na_mpesa_online(amount, phone_number)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
