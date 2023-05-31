import os

import stripe

stripe.api_key = os.getenv("STRIPE_API_KEY")

# def test_update_charge_send_reciept():
#     stripe.Charge.modify(
#         "ch_3NDtmGLa8xpi62wJ12KxhXAl",
#         receipt_email="dmhummel@gmail.com",
#         description='Thank you for supporting Promply.  Tap <a href="https://beta.promply.ai/?prs=728016dc-bb12-469e-bc89-b9c3ff5342ff">here to activate your tokens</a> on this device'
#     )
