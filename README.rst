==========================================================
django-celery-email - A Celery-backed Django Email Backend
==========================================================

.. image:: https://img.shields.io/travis/pmclanahan/django-celery-email/master.svg
    :target: https://travis-ci.org/pmclanahan/django-celery-email
.. image:: https://img.shields.io/pypi/v/django-celery-email.svg
    :target: https://pypi.python.org/pypi/django-celery-email

A `Django`_ email backend that uses a `Celery`_ queue for out-of-band sending
of the messages.

.. _`Celery`: http://celeryproject.org/
.. _`Django`: http://www.djangoproject.org/

.. warning::

	This version requires the following versions:

	* Python 2.7 and Python >= 3.5
	* Django 1.11, 2.1, and 2.2
	* Celery 4.0

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

Mass email are sent in chunks of size ``CELERY_EMAIL_CHUNK_SIZE`` (defaults to 10).

If you need to set any of the settings (attributes) you'd normally be able to set on a
`Celery Task`_ class had you written it yourself, you may specify them in a ``dict``
in the ``CELERY_EMAIL_TASK_CONFIG`` setting::

    CELERY_EMAIL_TASK_CONFIG = {
        'queue' : 'email',
        'rate_limit' : '50/m',  # * CELERY_EMAIL_CHUNK_SIZE (default: 10)
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
You should also set ``CELERY_EMAIL_CHUNK_SIZE = 1`` in settings if you are concerned about task status
and results.

See the `Celery docs`_ for more info.


``len(results)`` will be the number of emails you attempted to send divided by CELERY_EMAIL_CHUNK_SIZE, and is in no way a reflection on the success or failure
of their delivery.

.. _`Celery Task`: http://celery.readthedocs.org/en/latest/userguide/tasks.html#basics
.. _`Celery docs`: http://celery.readthedocs.org/en/latest/userguide/tasks.html#task-states
.. _`AsyncResult`: http://celery.readthedocs.org/en/latest/reference/celery.result.html#celery.result.AsyncResult

Changelog
=========

2.0.1 - 2018.18.27
------------------
* Fix bug preventing sending text/* encoded mime attachments. Thanks `Cesar Canassa`_.

.. _Cesar Canassa: https://github.com/canassa

2.0 - 2017.07.10
----------------
* Support for Django 1.11 and Celery 4.0
* Dropped support for Celery 2.x and 3.x
* Dropped support for Python 3.3

1.1.5 - 2016.07.20
------------------
* Support extra email attributes via CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES setting
* Updated version requirements in README


1.1.4 - 2016.01.19
------------------

* Support sending email with embedded images. Thanks `Georg Zimmer`_.
* Document CELERY_EMAIL_CHUNK_SIZE. Thanks `Jonas Haag`_.
* Add exception handling to email backend connection. Thanks `Tom`_.

.. _Georg Zimmer: https://github.com/georgmzimmer
.. _Tom: https://github.com/tomleo

1.1.3 - 2015.11.06
------------------

* Support setting celery.base from string. Thanks `Matthew Jacobi`_.
* Use six for py2/3 string compatibility. Thanks `Matthew Jacobi`_.
* Pass content_subtype back in for retries. Thanks `Mark Joshua Tan`_.
* Rework how tests work, add tox, rework travis-ci matrix.
* Use six from django.utils.
* Release a universal wheel.

.. _Matthew Jacobi: https://github.com/oppianmatt
.. _Mark Joshua Tan: https://github.com/mark-tan

1.1.2 - 2015.07.06
------------------

* Fix for HTML-only emails. Thanks `gnarvaja`_.

.. _gnarvaja: https://github.com/gnarvaja

1.1.1 - 2015.03.20
------------------

* Fix for backward compatibility of task kwarg handling - Thanks `Jeremy Thurgood`_.

.. _Jeremy Thurgood: https://github.com/jerith

1.1.0 - 2015.03.06
------------------

* New PyPI release rolling up 1.0.5 changes and some cleanup.
* More backward compatability in task. Will still accept message objects and lists of message objects.
* Thanks again to everyone who contributed to 1.0.5.

1.0.5 - 2014.08.24
------------------

* Django 1.6 support, Travis CI testing, chunked sending & more - thanks `Jonas Haag`_.
* HTML email support - thanks `Andres Riancho`_.
* Support for JSON transit for Celery, sponsored by `DigiACTive`_.
* Drop support for Django 1.2.

.. _`Jonas Haag`: https://github.com/jonashaag
.. _`Andres Riancho`: https://github.com/andresriancho
.. _`DigiACTive`: https://github.com/digiactive

1.0.4 - 2013.10.12
------------------

* Add Django 1.5.2 and Python 3 support.
* Thanks to `Stefan Wehrmeyer`_ for the contribution.

.. _`Stefan Wehrmeyer`: https://github.com/stefanw

1.0.3 - 2012.03.06
------------------

* Backend will now pass any kwargs with which it is initialized to the
  email sending backend.
* Thanks to `Fedor Tyurin`_ for the contribution.

.. _`Fedor Tyurin`: https://bitbucket.org/ftyurin


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
