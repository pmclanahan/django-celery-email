from django.conf import settings
from django.core import mail
from django.test import TestCase

from djcelery_email.tasks import send_email


class DjangoCeleryEmailTests(TestCase):

    def test_sending_email(self):
        mail.send_mail('test', 'Testing with Celery! w00t!!', 'from@example.com',
                       ['to@example.com'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test')

    def test_sending_mass_email(self):
        emails = (
            ('mass 1', 'mass message 1', 'from@example.com', ['to@example.com']),
            ('mass 2', 'mass message 2', 'from@example.com', ['to@example.com']),
        )
        results = mail.send_mass_mail(emails)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(mail.outbox[0].subject, 'mass 1')
        self.assertEqual(mail.outbox[1].subject, 'mass 2')
    
    def test_setting_extra_configs(self):
        self.assertEqual(send_email.queue, 'django_email')
        self.assertEqual(send_email.delivery_mode, 1)
        self.assertEqual(send_email.rate_limit, '50/m')
