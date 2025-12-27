import stripe
from fastapi import FastAPI, Request, HTTPException
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv('notapi.env')

app = FastAPI()

stripe.api_key = os.getenv("APIKEY")  
endpoint_secret = os.getenv("EPSEC")   

def send_file(email: str):
    msg = EmailMessage()
    msg["Subject"] = "Your Purchased File"
    msg["From"] = "saltbusinessmail@gmail.com"
    msg["To"] = email

    msg.set_content(
        """Thank you for your purchase!

Download your file here:
https://saltcourses.com/SaltMedia/pnpfull.pdf
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("GMAIL"), os.getenv("GMAILPASS"))
        smtp.send_message(msg)

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Only act on completed payments
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        if session["payment_status"] == "paid":
            email = session["customer_details"]["email"]
            send_file(email)

    return {"status": "ok"}
