from django.conf import settings
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase
from django.test.utils import override_settings
from django.core.mail.backends import locmem
from django.core.mail import EmailMultiAlternatives

import celery
from djcelery_email.tasks import send_email, send_emails
from djcelery_email.backends import to_dict
import djcelery_email


def even(n):
    return n % 2 == 0


def celery_queue_pop():
    """ Pops a single task from Celery's 'memory://' queue. """
    with celery.current_app.connection() as conn:
        queue = conn.SimpleQueue('django_email', no_ack=True)
        return queue.get().payload


class TracingBackend(BaseEmailBackend):
    def __init__(self, **kwargs):
        self.__class__.kwargs = kwargs

    def send_messages(self, messages):
        self.__class__.called = True


class TaskTests(TestCase):
    """
    Tests that the 'tasks.send_email(s)' task works correctly:
        - should accept a single or multiple messages (as dicts)
        - should send all these messages
        - should use the backend set in CELERY_EMAIL_BACKEND
        - should pass the given kwargs to that backend
        - should retry sending failed messages (see TaskErrorTests)
    """
    def test_send_single_email(self):
        """ It should accept and send a single EmailMessage object. """
        msg = mail.EmailMessage()
        send_email(to_dict(msg), backend_kwargs={})
        self.assertEqual(len(mail.outbox), 1)
        # we can't compare them directly as it's converted into a dict
        # for JSONification and then back. Compare dicts instead.
        self.assertEqual(to_dict(msg), to_dict(mail.outbox[0]))

    def test_send_multiple_emails(self):
        """ It should accept and send a list of EmailMessage objects. """
        N = 10
        msgs = [mail.EmailMessage() for i in range(N)]
        send_emails([to_dict(msg) for msg in msgs],
                    backend_kwargs={})

        self.assertEqual(len(mail.outbox), N)
        for i in range(N):
            self.assertEqual(to_dict(msgs[i]), to_dict(mail.outbox[i]))

    @override_settings(CELERY_EMAIL_BACKEND='tester.tests.TracingBackend')
    def test_uses_correct_backend(self):
        """ It should use the backend configured in CELERY_EMAIL_BACKEND. """
        TracingBackend.called = False
        msg = mail.EmailMessage()
        send_emails([to_dict(msg)], backend_kwargs={})
        self.assertTrue(TracingBackend.called)

    @override_settings(CELERY_EMAIL_BACKEND='tester.tests.TracingBackend')
    def test_backend_parameters(self):
        """ It should pass kwargs like username and password to the backend. """
        TracingBackend.kwargs = None
        msg = mail.EmailMessage()
        send_email(to_dict(msg), backend_kwargs={'foo': 'bar'})
        self.assertEqual(TracingBackend.kwargs.get('foo'), 'bar')


class EvenErrorBackend(locmem.EmailBackend):
    """ Fails to deliver every 2nd message. """
    def __init__(self, *args, **kwargs):
        super(EvenErrorBackend, self).__init__(*args, **kwargs)
        self.message_count = 0

    def send_messages(self, messages):
        self.message_count += 1
        if even(self.message_count-1):
            raise RuntimeError("Something went wrong sending the message")
        else:
            return super(EvenErrorBackend, self).send_messages(messages)


class TaskErrorTests(TestCase):
    """
    Tests that the 'tasks.send_emails' task does not crash if a single message
    could not be sent and that it requeues that message.
    """
    def setUp(self):
        super(TaskErrorTests, self).setUp()

        self._retry_calls = []
        def mock_retry(*args, **kwargs):
            self._retry_calls.append((args, kwargs))

        # TODO: replace with 'unittest.mock' at some point
        self._old_retry = send_emails.retry
        send_emails.retry = mock_retry

    def tearDown(self):
        super(TaskErrorTests, self).tearDown()
        send_emails.retry = self._old_retry

    @override_settings(CELERY_EMAIL_BACKEND='tester.tests.EvenErrorBackend')
    def test_send_multiple_emails(self):
        N = 10
        msgs = [mail.EmailMessage(subject="msg %d" % i) for i in range(N)]
        send_emails([to_dict(msg) for msg in msgs],
                     backend_kwargs={'foo': 'bar'})

        # Assert that only "odd"/good messages have been sent.
        self.assertEqual(len(mail.outbox), 5)
        self.assertEqual(
            [msg.subject for msg in mail.outbox],
            ["msg 1", "msg 3", "msg 5", "msg 7", "msg 9"]
        )

        # Assert that "even"/bad messages have been requeued,
        # one retry task per bad message.
        self.assertEqual(len(self._retry_calls), 5)
        odd_msgs = [msg for idx, msg in enumerate(msgs) if even(idx)]
        for msg, (args, kwargs) in zip(odd_msgs, self._retry_calls):
            retry_args = args[0]
            self.assertEqual(retry_args, [[to_dict(msg)], {'foo': 'bar'}])
            self.assertIsInstance(kwargs.get('exc'), RuntimeError)
            self.assertFalse(kwargs.get('throw', True))



class BackendTests(TestCase):
    """
    Tests that our *own* email backend ('backends.CeleryEmailBackend') works,
    i.e. it submits the correct number of jobs (according to the chunk size)
    and passes backend parameters to the task.
    """
    def test_backend_parameters(self):
        """ Our backend should pass kwargs to the 'send_emails' task. """
        kwargs = {'auth_user': 'user', 'auth_password': 'pass'}
        results = mail.send_mass_mail([
            ('test1', 'Testing with Celery! w00t!!', 'from@example.com', ['to@example.com']),
            ('test2', 'Testing with Celery! w00t!!', 'from@example.com', ['to@example.com'])
        ], **kwargs)

        args = celery_queue_pop()['args']
        self.assertEqual(len(args), 2)
        messages, backend_kwargs = args
        self.assertEqual(messages[0].subject, 'test1')
        self.assertEqual(messages[1].subject, 'test2')
        self.assertEqual(backend_kwargs, {'username': 'user', 'password': 'pass'})

    def test_chunking(self):
        """
        Given 11 messages and a chunk size of 4, the backend should queue
        11/4 = 3 jobs (2 jobs with 4 messages and 1 job with 3 messages).
        """
        N = 11
        chunksize = 4

        with override_settings(CELERY_EMAIL_CHUNK_SIZE=4):
            mail.send_mass_mail([
                ("subject", "body", "from@example.com", ["to@example.com"])
                for _ in range(N)
            ])

            num_chunks = 3  # floor(11.0 / 4.0)
            queued_tasks = [celery_queue_pop() for i in range(num_chunks)]
            full_tasks = queued_tasks[:-1]
            last_task = queued_tasks[-1]

            for task in full_tasks:
                self.assertEqual(len(task['args'][0]), chunksize)

            self.assertEqual(len(last_task['args'][0]), N % chunksize)


class ConfigTests(TestCase):
    """
    Tests that our Celery task has been initialized with the correct options
    (those set in the CELERY_EMAIL_TASK_CONFIG setting)
    """
    def test_setting_extra_configs(self):
        self.assertEqual(send_email.queue, 'django_email')
        self.assertEqual(send_email.delivery_mode, 1)
        self.assertEqual(send_email.rate_limit, '50/m')


@override_settings(CELERY_ALWAYS_EAGER=True)
class IntegrationTests(TestCase):
    def test_sending_email(self):
        results = mail.send_mail('test', 'Testing with Celery! w00t!!', 'from@example.com',
                                 ['to@example.com'])
        for result in results:
            result.get()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test')

    def test_sending_html_email(self):
        msg = EmailMultiAlternatives('test', 'Testing with Celery! w00t!!', 'from@example.com',
                                    ['to@example.com'])
        html = '<p>Testing with Celery! w00t!!</p>'
        msg.attach_alternative(html, 'text/html')
        results = msg.send()
        for result in results:
            result.get()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test')
        self.assertEqual(mail.outbox[0].alternatives, [(html, 'text/html')])

    def test_sending_mass_email(self):
        emails = (
            ('mass 1', 'mass message 1', 'from@example.com', ['to@example.com']),
            ('mass 2', 'mass message 2', 'from@example.com', ['to@example.com']),
        )
        results = mail.send_mass_mail(emails)
        for result in results:
            result.get()
        self.assertEqual(len(results), 1)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'mass 1')
        self.assertEqual(mail.outbox[1].subject, 'mass 2')
