from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_payment_confirmation_email(user_email, booking_id):
    subject = "Payment Confirmation"
    message = f"Your payment for booking {booking_id} was successful. Thank you!"
    send_mail(
        subject,
        message,
        'hello@kingsleyusa.dev',
        [user_email],
        fail_silently=False,
    )