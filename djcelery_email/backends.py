from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from djcelery_email.tasks import send_email


class CeleryEmailBackend(BaseEmailBackend):

    def send_messages(self, email_messages):
        results = []
        for msg in email_messages:
            results.append(send_email.delay(msg))
        return results
