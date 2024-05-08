from django.core.mail import send_mail

import random

def generate_otp(length=6):
    return ''.join(random.choice('0123456789') for _ in range(length))

def send_otp_email(email, otp):
    subject = 'Your OTP for Registration'
    message = f'Your OTP is: {otp}'
    from_email = 'abijithbca@gmail.com'
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)
