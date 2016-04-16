"""Custom log handler for posting log messages to Gitter"""

import logging

from util import log_to_gitter


class GitterHandler(logging.Handler):
    """Log handler used to send notifications to Gitter"""

    def emit(self, record):
        """Sends the record info to Gitter."""
        msg = str(self.format(record))
        if record.exc_info:
            exc = logging._defaultFormatter.formatException(record.exc_info)
            msg += "\n" + exc

        log_to_gitter(msg)
