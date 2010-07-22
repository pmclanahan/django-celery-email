from celery.task import Task
from django.core.mail import get_connection

CELERY_EMAIL_BACKEND = getattr(settings, 'CELERY_EMAIL_BACKEND',
                               'django.core.mail.backends.smtp.EmailBackend')


class SendEmailTask(Task):
    #default_retry_delay = 60 * 5
    ignore_result = True
    
    def run(self, message, **kwargs):
        logger = self.get_logger(**kwargs)
        conn = get_connection(backend=CELERY_EMAIL_BACKEND)
        try:
            conn.send_messages([message])
            logger.debug("Successfully sent email message to %r.", message.to)
        except:
            # catching all exceptions b/c it could be any number of things
            # depending on the backend
            try:
                self.retry([message], kwargs)
                logger.info("Failed to send email message to %r, retrying.",
                            message.to)
            except self.MaxRetriesExceededError:
                logger.error("Max retries exceeded trying to send email to %r.",
                             message.to)