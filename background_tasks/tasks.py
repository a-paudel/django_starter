from django.conf import settings
from django.core.mail import EmailMessage
from typing import Iterable
from huey.contrib.djhuey import task
from django.core import mail


@task()
def task_send_background_email(email_messages: Iterable[EmailMessage]):
    conn = mail.get_connection(settings.BACKGROUND_EMAIL_BACKEND)
    conn.send_messages(email_messages)
