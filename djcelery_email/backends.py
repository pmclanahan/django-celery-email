from django.core.mail.backends.base import BaseEmailBackend

from djcelery_email.tasks import send_email


def to_dict(message):
    return {'subject': message.subject,
            'body': message.body,
            'from_email': message.from_email,
            'to': message.to,
            'bcc': message.bcc,
            # ignore connection
            'attachments': message.attachments,
            'headers': message.extra_headers,
            'cc': message.cc,
            'alternatives': getattr(message, 'alternatives', None)}


class CeleryEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super(CeleryEmailBackend, self).__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, email_messages, **kwargs):
        results = []
        kwargs['_backend_init_kwargs'] = self.init_kwargs
        for msg in email_messages:
            results.append(send_email.delay(to_dict(msg), **kwargs))
        return results
