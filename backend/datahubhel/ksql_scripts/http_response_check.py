import logging

import requests

LOG = logging.getLogger(__name__)


def check_errors(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except Exception:
        try:
            data = response.json()
        except Exception:
            data = {}
        error_code = data.get("error_code")
        message = data.get("message")
        if error_code or message:
            LOG.error("Server returned error %r:\n%s", error_code, message)
        raise
