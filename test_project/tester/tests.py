from django.core import mail
from django.test import TestCase


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
        mail.send_mass_mail(emails)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'mass 1')
        self.assertEqual(mail.outbox[1].subject, 'mass 2')