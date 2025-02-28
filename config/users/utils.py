from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings

def send_sms(to, body):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_FROM_NUMBER

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body="salom zur",  # Message body
            from_="17722423567",  # Twilio phone number
            to="+998881353130"  # Recipient's phone number
        )
        print("SMS sent successfully! Message SID:", message.sid)
    except Exception as e:
        # Log or print the error for debugging
        print("Failed to send SMS. Error:", str(e))


def send_email(to_email, subject, message):

    try:
        send_mail(
            subject=subject,  # Email subject
            message=message,  # Email body
            from_email=settings.EMAIL_HOST_USER,  # Sender's email (defined in settings)
            recipient_list=[to_email],  # List of recipients
            fail_silently=False,  # Raise an error if sending fails
        )
        print("Email sent successfully!")
    except Exception as e:
        # Log or print the error for debugging
        print("Failed to send email. Error:", str(e))