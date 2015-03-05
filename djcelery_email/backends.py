from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from djcelery_email.tasks import send_emails
from djcelery_email.utils import chunked, to_dict_list


class CeleryEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super(CeleryEmailBackend, self).__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, email_messages):
        results = []
        for chunk in chunked(email_messages, settings.CELERY_EMAIL_CHUNK_SIZE):
            results.append(send_emails.delay(to_dict_list(chunk), self.init_kwargs))
        return results
