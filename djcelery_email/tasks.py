from django.conf import settings
from django.core.mail import get_connection

from celery.task import Task


CONFIG = getattr(settings, 'CELERY_EMAIL_TASK_CONFIG', {})
BACKEND = getattr(settings, 'CELERY_EMAIL_BACKEND',
                  'django.core.mail.backends.smtp.EmailBackend')


class SendEmailTask(Task):
    ignore_result = True
    
    def run(self, message, **kwargs):
        logger = self.get_logger(**kwargs)
        conn = get_connection(backend=BACKEND)
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

for key, val in CONFIG.iteritems():
    setattr(SendEmailTask, key, val)