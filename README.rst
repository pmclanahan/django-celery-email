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