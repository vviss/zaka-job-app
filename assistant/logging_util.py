import json
import logging
import sys

from config import LOG_LEVEL

_logger = logging.getLogger("assistant")

if not _logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


def log_request(context, payload):
    _logger.debug("%s request: %s", context, json.dumps(payload, default=str))


def log_event(message):
    _logger.info(message)


def log_error(message):
    _logger.error(message)
