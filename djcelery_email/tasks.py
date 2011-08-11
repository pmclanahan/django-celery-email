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
def send_email(message):
    logger = send_email.get_logger()
    conn = get_connection(backend=BACKEND)
    try:
        conn.send_messages([message])
        logger.debug("Successfully sent email message to %r.", message.to)
    except:
        # catching all exceptions b/c it could be any number of things
        # depending on the backend
        try:
            send_email.retry()
            logger.info("Failed to send email message to %r, retrying.",
                        message.to)
        except send_email.MaxRetriesExceededError:
            logger.error("Max retries exceeded trying to send email to %r.",
                         message.to)


# backwards compat
SendEmailTask = send_email
