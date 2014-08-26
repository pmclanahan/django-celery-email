from django.conf import settings
from django.core.mail import get_connection, EmailMessage, EmailMultiAlternatives

try:
    from celery import shared_task
except ImportError:
    from celery.decorators import task as shared_task

import djcelery_email.conf  # Make sure our AppConf is loaded properly.

# Messages *must* be dicts, not instances of the EmailMessage class
# This is because we expect Celery to use JSON encoding, and we want to prevent
# code assuming otherwise.

def from_dict(messagedict):
    if hasattr(messagedict, 'from_email'):
        raise ValueError("This appears to be an EmailMessage object, rather than a dictionary.")
    elif 'alternatives' in messagedict:
        return EmailMultiAlternatives(**messagedict)
    else:
        return EmailMessage(**messagedict)


TASK_CONFIG = {'name': 'djcelery_email_send_multiple', 'ignore_result': True}
TASK_CONFIG.update(settings.CELERY_EMAIL_TASK_CONFIG)


@shared_task(**TASK_CONFIG)
def send_emails(messages, backend_kwargs):

    # catch sending object
    if hasattr(messages, 'from_email'):
        raise ValueError("This appears to be an EmailMessage object, rather than a dictionary.")

    # catch send_email (not send_email*s*) case.
    if isinstance(messages, dict):
        messages = [messages]

    conn = get_connection(backend=settings.CELERY_EMAIL_BACKEND, **backend_kwargs)
    conn.open()

    for message in messages:
        try:
            conn.send_messages([from_dict(message)])
            logger.debug("Successfully sent email message to %r.", message['to'])
        except Exception as e:
            # Not expecting any specific kind of exception here because it
            # could be any number of things, depending on the backend
            logger.warning("Failed to send email message to %r, retrying. (%r)",
                           message['to'], e)
            send_emails.retry([[message], backend_kwargs], exc=e, throw=False)

    conn.close()


# backwards compatibility
SendEmailTask = send_email = send_emails


try:
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)
except ImportError:
    logger = send_emails.get_logger()
