import json
import logging

log = logging.getLogger(__name__)


def load(response):
    """Convert a response's binary data (JSON) to a dictionary."""
    text = response.data.decode('utf-8')

    if text:
        data = json.loads(text)
    else:
        data = None

    logging.debug("Response: %r", data)

    return data
