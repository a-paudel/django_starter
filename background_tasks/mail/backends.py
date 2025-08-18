from typing import Iterable
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
from django.core import mail
from django.conf import settings

from background_tasks.tasks import task_send_background_email


class BackgroundEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages: Iterable[EmailMessage]) -> int:
        task_send_background_email(email_messages)
        return 0
