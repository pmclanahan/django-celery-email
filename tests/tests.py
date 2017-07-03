import json
import os.path
from email.mime.image import MIMEImage

from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends import locmem
from django.core.mail import EmailMultiAlternatives
from django.test import TestCase
from django.test.utils import override_settings

import celery
from djcelery_email import tasks
from djcelery_email.utils import email_to_dict, dict_to_email


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


class UtilTests(TestCase):
    @override_settings(CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES=['extra_attribute'])
    def test_email_to_dict_extra_attrs(self):
        msg = mail.EmailMessage()
        msg.extra_attribute = {'name': 'val'}

        self.assertEquals(email_to_dict(msg)['extra_attribute'], msg.extra_attribute)

    @override_settings(CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES=['extra_attribute'])
    def test_dict_to_email_extra_attrs(self):
        msg_dict = email_to_dict(mail.EmailMessage())
        msg_dict['extra_attribute'] = {'name': 'val'}

        self.assertEquals(email_to_dict(dict_to_email(msg_dict)), msg_dict)

    def check_json_of_msg(self, msg):
        serialized = json.dumps(email_to_dict(msg))
        self.assertEqual(
            email_to_dict(dict_to_email(json.loads(serialized))),
            email_to_dict(msg))

    def test_email_with_attachment(self):
        file_path = os.path.join(os.path.dirname(__file__), 'image.png')
        with open(file_path, 'rb') as file:
            file_contents = file.read()
        msg = mail.EmailMessage(
            'test', 'Testing with Celery! w00t!!', 'from@example.com',
            ['to@example.com'])
        msg.attach('image.png', file_contents)
        self.check_json_of_msg(msg)

    def test_email_with_mime_attachment(self):
        file_path = os.path.join(os.path.dirname(__file__), 'image.png')
        with open(file_path, 'rb') as file:
            file_contents = file.read()
        mimg = MIMEImage(file_contents)
        msg = mail.EmailMessage(
            'test', 'Testing with Celery! w00t!!', 'from@example.com',
            ['to@example.com'])
        msg.attach(mimg)
        self.check_json_of_msg(msg)

    def test_email_with_attachment_from_file(self):
        file_path = os.path.join(os.path.dirname(__file__), 'image.png')
        msg = mail.EmailMessage(
            'test', 'Testing with Celery! w00t!!', 'from@example.com',
            ['to@example.com'])
        msg.attach_file(file_path)
        self.check_json_of_msg(msg)


class TaskTests(TestCase):
    """
    Tests that the 'tasks.send_email(s)' task works correctly:
        - should accept a single or multiple messages (as dicts)
        - should send all these messages
        - should use the backend set in CELERY_EMAIL_BACKEND
        - should pass the given kwargs to that backend
        - should retry sending failed messages (see TaskErrorTests)
    """
    def test_send_single_email_object(self):
        """ It should accept and send a single EmailMessage object. """
        msg = mail.EmailMessage()
        tasks.send_email(msg, backend_kwargs={})
        self.assertEqual(len(mail.outbox), 1)
        # we can't compare them directly as it's converted into a dict
        # for JSONification and then back. Compare dicts instead.
        self.assertEqual(email_to_dict(msg), email_to_dict(mail.outbox[0]))

    def test_send_single_email_object_no_backend_kwargs(self):
        """ It should send email with backend_kwargs not provided. """
        msg = mail.EmailMessage()
        tasks.send_email(msg)
        self.assertEqual(len(mail.outbox), 1)
        # we can't compare them directly as it's converted into a dict
        # for JSONification and then back. Compare dicts instead.
        self.assertEqual(email_to_dict(msg), email_to_dict(mail.outbox[0]))

    def test_send_single_email_object_response(self):
        """ It should return the number of messages sent, 1 here. """
        msg = mail.EmailMessage()
        messages_sent = tasks.send_email(msg)
        self.assertEqual(messages_sent, 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_single_email_dict(self):
        """ It should accept and send a single EmailMessage dict. """
        msg = mail.EmailMessage()
        tasks.send_email(email_to_dict(msg), backend_kwargs={})
        self.assertEqual(len(mail.outbox), 1)
        # we can't compare them directly as it's converted into a dict
        # for JSONification and then back. Compare dicts instead.
        self.assertEqual(email_to_dict(msg), email_to_dict(mail.outbox[0]))

    def test_send_multiple_email_objects(self):
        """ It should accept and send a list of EmailMessage objects. """
        N = 10
        msgs = [mail.EmailMessage() for i in range(N)]
        tasks.send_emails([email_to_dict(msg) for msg in msgs],
                          backend_kwargs={})

        self.assertEqual(len(mail.outbox), N)
        for i in range(N):
            self.assertEqual(email_to_dict(msgs[i]), email_to_dict(mail.outbox[i]))

    def test_send_multiple_email_dicts(self):
        """ It should accept and send a list of EmailMessage dicts. """
        N = 10
        msgs = [mail.EmailMessage() for i in range(N)]
        tasks.send_emails(msgs, backend_kwargs={})

        self.assertEqual(len(mail.outbox), N)
        for i in range(N):
            self.assertEqual(email_to_dict(msgs[i]), email_to_dict(mail.outbox[i]))

    def test_send_multiple_email_dicts_response(self):
        """ It should return the number of messages sent. """
        N = 10
        msgs = [mail.EmailMessage() for i in range(N)]
        messages_sent = tasks.send_emails(msgs, backend_kwargs={})
        self.assertEqual(messages_sent, N)
        self.assertEqual(len(mail.outbox), N)

    @override_settings(CELERY_EMAIL_BACKEND='tests.tests.TracingBackend')
    def test_uses_correct_backend(self):
        """ It should use the backend configured in CELERY_EMAIL_BACKEND. """
        TracingBackend.called = False
        msg = mail.EmailMessage()
        tasks.send_email(email_to_dict(msg), backend_kwargs={})
        self.assertTrue(TracingBackend.called)

    @override_settings(CELERY_EMAIL_BACKEND='tests.tests.TracingBackend')
    def test_backend_parameters(self):
        """ It should pass kwargs like username and password to the backend. """
        TracingBackend.kwargs = None
        msg = mail.EmailMessage()
        tasks.send_email(email_to_dict(msg), backend_kwargs={'foo': 'bar'})
        self.assertEqual(TracingBackend.kwargs.get('foo'), 'bar')

    @override_settings(CELERY_EMAIL_BACKEND='tests.tests.TracingBackend')
    def test_backend_parameters_kwargs(self):
        """ It should pass on kwargs specified as keyword params. """
        TracingBackend.kwargs = None
        msg = mail.EmailMessage()
        tasks.send_email(email_to_dict(msg), foo='bar')
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
    # TODO: replace setUp/tearDown with 'unittest.mock' at some point
    def setUp(self):
        super(TaskErrorTests, self).setUp()

        self._retry_calls = []

        def mock_retry(*args, **kwargs):
            self._retry_calls.append((args, kwargs))

        self._old_retry = tasks.send_emails.retry
        tasks.send_emails.retry = mock_retry

    def tearDown(self):
        super(TaskErrorTests, self).tearDown()
        tasks.send_emails.retry = self._old_retry

    @override_settings(CELERY_EMAIL_BACKEND='tests.tests.EvenErrorBackend')
    def test_send_multiple_emails(self):
        N = 10
        msgs = [mail.EmailMessage(subject="msg %d" % i) for i in range(N)]
        tasks.send_emails([email_to_dict(msg) for msg in msgs],
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
            self.assertEqual(retry_args, [[email_to_dict(msg)], {'foo': 'bar'}])
            self.assertTrue(isinstance(kwargs.get('exc'), RuntimeError))
            self.assertFalse(kwargs.get('throw', True))


class BackendTests(TestCase):
    """
    Tests that our *own* email backend ('backends.CeleryEmailBackend') works,
    i.e. it submits the correct number of jobs (according to the chunk size)
    and passes backend parameters to the task.
    """
    # TODO: replace setUp/tearDown with 'unittest.mock' at some point
    def setUp(self):
        super(BackendTests, self).setUp()

        self._delay_calls = []

        def mock_delay(*args, **kwargs):
            self._delay_calls.append((args, kwargs))

        self._old_delay = tasks.send_emails.delay
        tasks.send_emails.delay = mock_delay

    def tearDown(self):
        super(BackendTests, self).tearDown()
        tasks.send_emails.delay = self._old_delay

    def test_backend_parameters(self):
        """ Our backend should pass kwargs to the 'send_emails' task. """
        kwargs = {'auth_user': 'user', 'auth_password': 'pass'}
        mail.send_mass_mail([
            ('test1', 'Testing with Celery! w00t!!', 'from@example.com', ['to@example.com']),
            ('test2', 'Testing with Celery! w00t!!', 'from@example.com', ['to@example.com'])
        ], **kwargs)

        self.assertEqual(len(self._delay_calls), 1)
        args, kwargs = self._delay_calls[0]
        messages, backend_kwargs = args
        self.assertEqual(messages[0]['subject'], 'test1')
        self.assertEqual(messages[1]['subject'], 'test2')
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
            self.assertEqual(len(self._delay_calls), num_chunks)

            full_tasks = self._delay_calls[:-1]
            last_task = self._delay_calls[-1]

            for args, kwargs in full_tasks:
                self.assertEqual(len(args[0]), chunksize)

            args, kwargs = last_task
            self.assertEqual(len(args[0]), N % chunksize)


class ConfigTests(TestCase):
    """
    Tests that our Celery task has been initialized with the correct options
    (those set in the CELERY_EMAIL_TASK_CONFIG setting)
    """
    def test_setting_extra_configs(self):
        self.assertEqual(tasks.send_email.queue, 'django_email')
        self.assertEqual(tasks.send_email.delivery_mode, 1)
        self.assertEqual(tasks.send_email.rate_limit, '50/m')


class IntegrationTests(TestCase):
    # We run these tests in ALWAYS_EAGER mode, but they might as well be
    # executed using a real backend (maybe we can add that to the test setup in
    # the future?)

    def setUp(self):
        super(IntegrationTests, self).setUp()
        # TODO: replace with 'unittest.mock' at some point
        celery.current_app.conf.task_always_eager = True

    def tearDown(self):
        super(IntegrationTests, self).tearDown()
        celery.current_app.conf.task_always_eager = False

    def test_sending_email(self):
        [result] = mail.send_mail('test', 'Testing with Celery! w00t!!', 'from@example.com',
                                  ['to@example.com'])
        self.assertEqual(result.get(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test')

    def test_sending_html_email(self):
        msg = EmailMultiAlternatives('test', 'Testing with Celery! w00t!!', 'from@example.com',
                                     ['to@example.com'])
        html = '<p>Testing with Celery! w00t!!</p>'
        msg.attach_alternative(html, 'text/html')
        [result] = msg.send()
        self.assertEqual(result.get(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test')
        self.assertEqual(mail.outbox[0].alternatives, [(html, 'text/html')])

    def test_sending_html_only_email(self):
        msg = mail.EmailMessage('test', 'Testing <b>with Celery! w00t!!</b>', 'from@example.com',
                                ['to@example.com'])
        msg.content_subtype = "html"
        [result] = msg.send()
        self.assertEqual(result.get(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test')
        self.assertEqual(mail.outbox[0].content_subtype, "html")

    def test_sending_mass_email(self):
        emails = (
            ('mass 1', 'mass message 1', 'from@example.com', ['to@example.com']),
            ('mass 2', 'mass message 2', 'from@example.com', ['to@example.com']),
        )
        [result] = mail.send_mass_mail(emails)
        self.assertEqual(result.get(), 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'mass 1')
        self.assertEqual(mail.outbox[1].subject, 'mass 2')

    def test_sending_mass_email_chunked(self):
        emails = [
            ('mass %i' % i, 'message', 'from@example.com', ['to@example.com'])
            for i in range(11)]
        with override_settings(CELERY_EMAIL_CHUNK_SIZE=4):
            [result1, result2, result3] = mail.send_mass_mail(emails)
            self.assertEqual(result1.get(), 4)
            self.assertEqual(result2.get(), 4)
            self.assertEqual(result3.get(), 3)
            self.assertEqual(len(mail.outbox), 11)
            self.assertEqual(mail.outbox[0].subject, 'mass 0')
            self.assertEqual(mail.outbox[1].subject, 'mass 1')
