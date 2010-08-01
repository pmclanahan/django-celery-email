=================================================
django-celery-email - Django Celery Email Backend
=================================================

A `Django`_ 1.2+ email backend that uses a `Celery`_ queue for out-of-band sending
of the messages.

.. _`Celery`: http://celeryproject.org/
.. _`Django`: http://www.djangoproject.org/

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

After this setup is complete, and you have a working Celery install, sending
email will work exactly like it did before, except that the sending will be
handled by your Celery workers.

.. _`Celery Task`: http://celeryq.org/docs/reference/celery.task.base.html#defining-tasks-celery-task-base