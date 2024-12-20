from django.core.mail import send_mail
from django.conf import settings

def send_notification_email(user, subject, message):
    """
    Envía un correo electrónico de notificación al usuario.
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )