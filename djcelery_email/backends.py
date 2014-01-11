from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from djcelery_email.tasks import send_emails


def chunked(iterator, chunksize):
    """
    Yields items from 'iterator' in chunks of size 'chunksize'.

    >>> list(chunked([1, 2, 3, 4, 5], chunksize=2))
    [(1, 2), (3, 4), (5,)]
    """
    chunk = []
    for idx, item in enumerate(iterator, 1):
        chunk.append(item)
        if idx % chunksize == 0:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def to_dict(message):
    message_dict = {'subject': message.subject,
                    'body': message.body,
                    'from_email': message.from_email,
                    'to': message.to,
                    'bcc': message.bcc,
                    # ignore connection
                    'attachments': message.attachments,
                    'headers': message.extra_headers,
                    'cc': message.cc}

    if hasattr(message, 'alternatives'):
        message_dict['alternatives'] = message.alternatives

    return message_dict


class CeleryEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super(CeleryEmailBackend, self).__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, email_messages):
        result_tasks = []
        messages = [to_dict(msg) for msg in email_messages]
        for chunk in chunked(messages, settings.CELERY_EMAIL_CHUNK_SIZE):
            result_tasks.append(send_emails.delay(chunk, self.init_kwargs))
        return result_tasks
