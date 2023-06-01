import os

import stripe

stripe.api_key = os.getenv("STRIPE_API_KEY")

# def test_update_charge_send_reciept():
#     stripe.Charge.modify(
#         "py_3NE0aFLa8xpi62wJ1UHX6768",
#         receipt_email="jonathan.bengtson@gmail.com",
#         description='Thank you for supporting Promply.  Tap <a href="https://beta.promply.ai/?prs=68685693-0871-4315-b8d3-1e513b1d7443">here to activate your tokens</a> on this device'
#     )
