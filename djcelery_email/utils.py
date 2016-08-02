import copy
import base64
from email.mime.base import MIMEBase

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage


def chunked(iterator, chunksize):
    """
    Yields items from 'iterator' in chunks of size 'chunksize'.

    >>> list(chunked([1, 2, 3, 4, 5], chunksize=2))
    [(1, 2), (3, 4), (5,)]
    """
    chunk = []
    for idx, item in enumerate(iterator, 1):
        chunk.append(item)
        if idx % chunksize == 0:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def email_to_dict(message):
    if isinstance(message, dict):
        return message

    message_dict = {'subject': message.subject,
                    'body': message.body,
                    'from_email': message.from_email,
                    'to': message.to,
                    'bcc': message.bcc,
                    # ignore connection
                    'attachments': [],
                    'headers': message.extra_headers,
                    'cc': message.cc}

    # Django 1.8 support
    # https://docs.djangoproject.com/en/1.8/topics/email/#django.core.mail.EmailMessage
    if hasattr(message, 'reply_to'):
        message_dict['reply_to'] = message.reply_to

    if hasattr(message, 'alternatives'):
        message_dict['alternatives'] = message.alternatives
    if message.content_subtype != EmailMessage.content_subtype:
        message_dict["content_subtype"] = message.content_subtype
    if message.mixed_subtype != EmailMessage.mixed_subtype:
        message_dict["mixed_subtype"] = message.mixed_subtype

    attachments = message.attachments
    for attachment in attachments:
        if isinstance(attachment, MIMEBase):
            filename = attachment.get_filename('')
            binary_contents = attachment.get_payload(decode=True)
            mimetype = attachment.get_content_type()
        else:
            filename, binary_contents, mimetype = attachment
        contents = base64.b64encode(binary_contents).decode('ascii')
        message_dict['attachments'].append((filename, contents, mimetype))

    if settings.CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES:
        for attr in settings.CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES:
            if hasattr(message, attr):
                message_dict[attr] = getattr(message, attr)

    return message_dict


def dict_to_email(messagedict):
    messagedict = copy.deepcopy(messagedict)
    extra_attrs = {}
    if settings.CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES:
        for attr in settings.CELERY_EMAIL_MESSAGE_EXTRA_ATTRIBUTES:
            if attr in messagedict:
                extra_attrs[attr] = messagedict.pop(attr)
    attachments = messagedict.pop('attachments')
    messagedict['attachments'] = []
    for attachment in attachments:
        filename, contents, mimetype = attachment
        binary_contents = base64.b64decode(contents.encode('ascii'))
        messagedict['attachments'].append(
            (filename, binary_contents, mimetype))
    if isinstance(messagedict, dict) and "content_subtype" in messagedict:
        content_subtype = messagedict["content_subtype"]
        del messagedict["content_subtype"]
    else:
        content_subtype = None
    if isinstance(messagedict, dict) and "mixed_subtype" in messagedict:
        mixed_subtype = messagedict["mixed_subtype"]
        del messagedict["mixed_subtype"]
    else:
        mixed_subtype = None
    if hasattr(messagedict, 'from_email'):
        ret = messagedict
    elif 'alternatives' in messagedict:
        ret = EmailMultiAlternatives(**messagedict)
    else:
        ret = EmailMessage(**messagedict)
    for attr, val in extra_attrs.items():
        setattr(ret, attr, val)
    if content_subtype:
        ret.content_subtype = content_subtype
        messagedict["content_subtype"] = content_subtype  # bring back content subtype for 'retry'
    if mixed_subtype:
        ret.mixed_subtype = mixed_subtype
        messagedict["mixed_subtype"] = mixed_subtype  # bring back mixed subtype for 'retry'

    return ret
