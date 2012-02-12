from django.conf import settings
from django.core.mail import get_connection

from celery.task import task


CONFIG = getattr(settings, 'CELERY_EMAIL_TASK_CONFIG', {})
BACKEND = getattr(settings, 'CELERY_EMAIL_BACKEND',
                  'django.core.mail.backends.smtp.EmailBackend')
TASK_CONFIG = {
    'name': 'djcelery_email_send',
    'ignore_result': True,
}
TASK_CONFIG.update(CONFIG)


@task(**TASK_CONFIG)
def send_email(message, **kwargs):
    logger = send_email.get_logger()
    conn = get_connection(backend=BACKEND)
    try:
        result = conn.send_messages([message])
        logger.debug("Successfully sent email message to %r.", message.to)
        return result
    except Exception, e:
        # catching all exceptions b/c it could be any number of things
        # depending on the backend
        logger.warning("Failed to send email message to %r, retrying.",
                    message.to)
        send_email.retry(exc=e)


# backwards compat
SendEmailTask = send_email
