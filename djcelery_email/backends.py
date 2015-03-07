from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from djcelery_email.tasks import send_emails
from djcelery_email.utils import chunked, email_to_dict


class CeleryEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super(CeleryEmailBackend, self).__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, email_messages):
        result_tasks = []
        messages = [email_to_dict(msg) for msg in email_messages]
        for chunk in chunked(messages, settings.CELERY_EMAIL_CHUNK_SIZE):
            result_tasks.append(send_emails.delay(chunk, self.init_kwargs))
        return result_tasks
