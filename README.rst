==========================================================
django-celery-email - A Celery-backed Django Email Backend
==========================================================

A `Django`_ 1.2+ email backend that uses a `Celery`_ queue for out-of-band sending
of the messages.

.. _`Celery`: http://celeryproject.org/
.. _`Django`: http://www.djangoproject.org/

.. warning::
	
	This version of ``django-celery-email`` is NOT compatible with versions
	of Celery prior to 2.2.0. If you need to use Celery 2.0.x or 2.1.x, please
	use `django-celery-email 0.1.1`_.

.. _`django-celery-email 0.1.1`: http://pypi.python.org/pypi/django-celery-email/0.1.1/

Using django-celery-email
=========================

To enable ``django-celery-email`` for your project you need to add ``djcelery_email`` to
``INSTALLED_APPS``::

    INSTALLED_APPS += ("djcelery_email",)

You must then set ``django-celery-email`` as your ``EMAIL_BACKEND``::

    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

By default ``django-celery-email`` will use Django's builtin ``SMTP`` email backend
for the actual sending of the mail. If you'd like to use another backend, you
may set it in ``CELERY_EMAIL_BACKEND`` just like you would normally have set
``EMAIL_BACKEND`` before you were using Celery. In fact, the normal installation
procedure will most likely be to get your email working using only Django, then
change ``EMAIL_BACKEND`` to ``CELERY_EMAIL_BACKEND``, and then add the new
``EMAIL_BACKEND`` setting from above.

If you need to set any of the settings (attributes) you'd normally be able to set on a
`Celery Task`_ class had you written it yourself, you may specify them in a ``dict``
in the ``CELERY_EMAIL_TASK_CONFIG`` setting::

    CELERY_EMAIL_TASK_CONFIG = {
        'queue' : 'email',
        'rate_limit' : '50/m',
        ...
    }

There are some default settings. Unless you specify otherwise, the equivalent of the
following settings will apply::

    CELERY_EMAIL_TASK_CONFIG = {
        'name': 'djcelery_email_send',
        'ignore_result': True,
    }

After this setup is complete, and you have a working Celery install, sending
email will work exactly like it did before, except that the sending will be
handled by your Celery workers::

    from django.core import mail

    emails = (
        ('Hey Man', "I'm The Dude! So that's what you call me.", 'dude@aol.com', ['mr@lebowski.com']),
        ('Dammit Walter', "Let's go bowlin'.", 'dude@aol.com', ['wsobchak@vfw.org']),
    )
    results = mail.send_mass_mail(emails)

``results`` will be a list of celery `AsyncResult`_ objects that you may ignore, or use to check the
status of the email delivery task, or even wait for it to complete if want. You have to enable a result
backend and set ``ignore_result`` to ``False`` in ``CELERY_EMAIL_TASK_CONFIG`` if you want to use these.
See the `Celery docs`_ for more info.

``len(results)`` will be the number of emails you attempted to send, and is in no way a reflection on the success or failure 
of their delivery.

.. _`Celery Task`: http://celery.readthedocs.org/en/latest/userguide/tasks.html#basics
.. _`Celery docs`: http://celery.readthedocs.org/en/latest/userguide/tasks.html#task-states
.. _`AsyncResult`: http://celery.readthedocs.org/en/latest/reference/celery.result.html#celery.result.AsyncResult

Changelog
=========

1.0.2 - 2012.02.21
------------------

* Task and backend now accept kwargs that can be used in signal handlers.
* Task now returns the result from the email sending backend.
* Thanks to `Yehonatan Daniv`_ for these changes.

.. _`Yehonatan Daniv`: https://bitbucket.org/ydaniv

1.0.1 - 2011.10.06
------------------

* Fixed a bug that resulted in tasks that were throwing errors reporting success.
* If there is an exception thrown by the sending email backend, the result of the task will
  now be this exception.
