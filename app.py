# app.py
#
# Use this sample code to handle webhook events in your integration.
#
# 1) Paste this code into a new file (app.py)
#
# 2) Install dependencies
#   pip3 install flask
#   pip3 install stripe
#
# 3) Run the server on http://localhost:4242
#   python3 -m flask run --port=4242

import json
import logging
import os

import stripe
from flask import Flask, jsonify, request
from psycopg.errors import UniqueViolation

import db_utils as du

api_key = os.getenv("STRIPE_API_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SIGNATURE")
token_db_connection = os.getenv("TOKEN_DB_CONNECTION")
log_level = os.getenv("LOGGING_LEVEL","INFO")

numeric_level = getattr(logging, log_level.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % log_level)
logging.basicConfig(level=numeric_level, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

du.set_token_db_connection(token_db_connection)

app = Flask(__name__)

TOKEN_COUNTS = {100:5,500:30,1000:80}


@app.route('/healthz')
def healthz():
    return 'OK'


@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
    except:
        print('⚠️  Webhook error while parsing basic request.' + str(event))
        return jsonify(success=False)
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # Handle the event
    if event and event['type'] == 'charge.succeeded':
        payment_intent = event['data']['object']
        amount = payment_intent['amount']
        name = payment_intent['billing_details']['name']
        email = payment_intent['billing_details']['email']
        phone = payment_intent['billing_details']['phone']
        contact_id = email if email else phone
        logging.info (f"Charge succeeded webhook called for ${amount} - Name: {name}, Email: {email}, Phone: {phone}")
        try:
            du.create_account(contact_id, name, name)
            logging.info(f"Created account for - contact_id:{contact_id} Name: {name}, Email: {email}, Phone: {phone}")
        except UniqueViolation as e:
            logging.info(f"Account already exists for - contact_id:{contact_id} Name: {name}, Email: {email}, Phone: {phone}")

        token_count = TOKEN_COUNTS.get(amount)

        if token_count is None:
            logging.error(f"UNCOMPENSATED PAYMENT : Unexpected amount {amount} received from {contact_id}")
            return

        if not du.add_tokens(contact_id,token_count):
            logging.error(f"UNCOMPENSATED PAYMENT : Failed to give {token_count} tokens to {contact_id}")
            return



    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)
