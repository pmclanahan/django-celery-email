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
                    'attachments': message.attachments,
                    'headers': message.extra_headers,
                    'cc': message.cc}

    if hasattr(message, 'alternatives'):
        message_dict['alternatives'] = message.alternatives

    return message_dict


def dict_to_email(messagedict):
    if hasattr(messagedict, 'from_email'):
        return messagedict
    elif 'alternatives' in messagedict:
        return EmailMultiAlternatives(**messagedict)
    else:
        return EmailMessage(**messagedict)
