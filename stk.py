from flask import Flask, request, jsonify, render_template
import requests
import json
from requests.auth import HTTPBasicAuth
import datetime

app = Flask(__name__)

# Replace with your credentials
CONSUMER_KEY = 'sTFmEBfTSz6jg0AOFuB2GoSvy3sFMSIPXBRIcDYdZGu3KfzH'
CONSUMER_SECRET = ' iiT9sSspIQHp8Po4Gvv7zIl5k1yfeGqSNZrF50IiZ7GGeDHt5R0JWlBG1mA59V4Z'
SHORTCODE = '894624'
PASSKEY = 'your_passkey'
LIPA_NA_MPESA_ONLINE_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

def get_access_token():
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    return json.loads(response.text)['access_token']

@app.route('/pay_fees/<admission_no>', methods=['GET', 'POST'])
def pay_fees(admission_no):
    if request.method == 'POST':
        amount = request.form['amount']
        phone_number = request.form['phone_number']

        access_token = get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password = f"{SHORTCODE}{PASSKEY}{timestamp}".encode('utf-8')
        password = password.hex()

        payload = {
            'BusinessShortCode': SHORTCODE,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': SHORTCODE,
            'PhoneNumber': phone_number,
            'CallBackURL': 'https://example.com',
            'AccountReference': admission_no,
            'TransactionDesc': 'Fee payment',
        }

        response = requests.post(LIPA_NA_MPESA_ONLINE_URL, headers=headers, json=payload)
        return response.json()

    return render_template('pay_fees.html', admission_no=admission_no)

@app.route('/mpesa_callback', methods=['POST'])
def mpesa_callback():
    data = request.json
    # Example of how to extract data
    if data['Body']['stkCallback']['ResultCode'] == 0:
        amount_paid = data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        return render_template('payment_success.html', amount=amount_paid)
    else:
        return "Payment failed", 400

if __name__ == '__main__':
    app.run(debug=True)
