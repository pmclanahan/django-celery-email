from django.core.mail import EmailMessage


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


def to_dict_list(messages):
    """Return EmailMessage objects as a list of dicts."""
    if hasattr(messages, 'from_email'):
        # looks like a single EmailMessage object
        messages = [messages]

    message_dicts = []
    for message in messages:
        message_dicts.append({
            'subject': message.subject,
            'body': message.body,
            'from_email': message.from_email,
            'to': message.to,
            'bcc': message.bcc,
            # ignore connection
            'attachments': message.attachments,
            'headers': message.extra_headers,
            'cc': message.cc,
        })

    return message_dicts


def from_dict_list(messages):
    if len(messages) > 0 and hasattr(messages[0], 'from_email'):
        # list of EmailMessage objects already. bail.
        return messages

    return [EmailMessage(**m) for m in messages]
