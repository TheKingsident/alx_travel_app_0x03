from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_confirmation_email(user_email, booking_id):
    """Send payment confirmation email after successful payment"""
    subject = "Payment Confirmation - ALX Travel App"
    message = f"""
    Dear Customer,

    Your payment for booking #{booking_id} has been successfully processed. 
    Thank you for choosing ALX Travel App!

    We hope you have a wonderful stay.

    Best regards,
    ALX Travel App Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return f"Payment confirmation email sent to {user_email} for booking {booking_id}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

@shared_task
def send_booking_confirmation_email(user_email, booking_id, listing_title, start_date, end_date):
    """Send booking confirmation email when a booking is created"""
    subject = "Booking Confirmation - ALX Travel App"
    message = f"""
    Dear Customer,

    Your booking has been confirmed!

    Booking Details:
    - Booking ID: #{booking_id}
    - Property: {listing_title}
    - Check-in: {start_date}
    - Check-out: {end_date}

    Please complete your payment to secure your reservation.

    Best regards,
    ALX Travel App Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return f"Booking confirmation email sent to {user_email} for booking {booking_id}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"