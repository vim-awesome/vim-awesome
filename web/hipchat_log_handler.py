"""Custom log handler for posting log messages to HipChat.

Adapted from https://gist.github.com/3176710

The API documentation is available at
https://www.hipchat.com/docs/api/method/rooms/message

The room id can be found by going to
https://{{your-account}}.hipchat.com/rooms/ids

The tokens can be set at https://{{your-account}}.hipchat.com/admin/api

Dependencies: Requests (http://docs.python-requests.org)
"""

import logging
import sys

import requests


class HipChatHandler(logging.Handler):
    """Log handler used to send notifications to HipChat"""

    HIPCHAT_API_URL = 'https://api.hipchat.com/v1/rooms/message'

    def __init__(self, token, room,
                sender='Flask', notify=False, color='yellow', colors={}):
        """
        :param token: the auth token for access to the API - see hipchat.com
        :param room: the numerical id of the room to send the message to
        :param sender (optional): the 'from' property of the message - appears
            in the HipChat window
        :param notify (optional): if True, HipChat pings / bleeps / flashes
            when message is received
        :param color (optional): sets the background color of the message in
            the HipChat window
        :param colors (optional): a dict of level:color pairs (eg.
            {'DEBUG:'red'} used to override the default color)
        """
        logging.Handler.__init__(self)
        self.token = token
        self.room = room
        self.sender = sender
        self.notify = notify
        self.color = color
        self.colors = colors

    def emit(self, record):
        """Sends the record info to HipChat."""
        if not self.token:
            return

        try:
            # use a custom level-based color from self.colors, if it exists in
            # the dict
            color = self.colors.get(record.levelname, self.color)

            msg = str(self.format(record))
            if record.exc_info:
                msg += "\n%s" % logging._defaultFormatter.formatException(
                        record.exc_info)

            r = self._sendToHipChat(msg, color, self.notify)

            # use print, not logging, as that would introduce a circular
            # reference
            print 'Message sent to room {0}: {1}\nResponse: {2}'.format(
                self.room, record.getMessage(), r.text)
        except:
            print sys.exc_info()[1]
            self.handleError(record)

    def _sendToHipChat(self, msg, color, notify):
        """Does the actual sending of the message."""
        payload = {
            'auth_token': self.token,
            'notify': 1 if notify else 0,
            'color': color,
            'from': self.sender,
            'room_id': self.room,
            'message': msg,
            'message_format': 'text',
        }

        return requests.post(self.HIPCHAT_API_URL, data=payload)
