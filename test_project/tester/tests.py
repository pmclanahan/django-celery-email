from django.conf import settings
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase

from djcelery_email.tasks import send_email
import djcelery_email


class TestBackend(BaseEmailBackend):
    def __init__(self, username=None, password=None, fail_silently=False, **kwargs):
        self.username = username
        self.password = password

    def send_messages(self, email_messages):
        return {'username': self.username, 'password': self.password}


class DjangoCeleryEmailTests(TestCase):

    def test_sending_email(self):
        results = mail.send_mail('test', 'Testing with Celery! w00t!!', 'from@example.com',
                                 ['to@example.com'])
        for result in results:
            result.get()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test')

    def test_sending_mass_email(self):
        emails = (
            ('mass 1', 'mass message 1', 'from@example.com', ['to@example.com']),
            ('mass 2', 'mass message 2', 'from@example.com', ['to@example.com']),
        )
        results = mail.send_mass_mail(emails)
        for result in results:
            result.get()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(mail.outbox[0].subject, 'mass 1')
        self.assertEqual(mail.outbox[1].subject, 'mass 2')

    def test_setting_extra_configs(self):
        self.assertEqual(send_email.queue, 'django_email')
        self.assertEqual(send_email.delivery_mode, 1)
        self.assertEqual(send_email.rate_limit, '50/m')

    def test_backend_parameters(self):
        # Set test backend
        default_backend = djcelery_email.tasks.BACKEND
        djcelery_email.tasks.BACKEND = 'test_project.tester.tests.TestBackend'
        # Actual test
        results = mail.send_mail('test', 'Testing with Celery! w00t!!', 'from@example.com',
                                 ['to@example.com'], auth_user='username', auth_password='password')
        for result in results:
            self.assertEqual(result.get(), {'username': 'username', 'password': 'password'})
        # Restore backend
        djcelery_email.tasks.BACKEND = default_backend
