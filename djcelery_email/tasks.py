from django.conf import settings
from django.core.mail import get_connection

try:
    from celery import shared_task
except ImportError:
    from celery.decorators import task as shared_task

import djcelery_email.conf  # Make sure our AppConf is loaded properly.


TASK_CONFIG = {'name': 'djcelery_email_send_multiple', 'ignore_result': True}
TASK_CONFIG.update(settings.CELERY_EMAIL_TASK_CONFIG)


@shared_task(**TASK_CONFIG)
def send_emails(messages, backend_kwargs):
    if hasattr(messages, 'from_email'):
        # backwards compatibility: looks like a EmailMessage object
        messages = [messages]

    conn = get_connection(backend=settings.CELERY_EMAIL_BACKEND, **backend_kwargs)

    for message in messages:
        try:
            conn.send_messages([message])
            logger.debug("Successfully sent email message to %r.", message.to)
        except Exception as e:
            # Not expecting any specific kind of exception here because it
            # could be any number of things, depending on the backend
            logger.warning("Failed to send email message to %r, retrying. (%r)",
                           message.to, e)
            send_emails.retry([[message], backend_kwargs], exc=e, throw=False)


# backwards compatibility
SendEmailTask = send_email = send_emails


try:
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)
except ImportError:
    logger = send_emails.get_logger()
