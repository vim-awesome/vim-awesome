"""Sends a message to HipChat that we just deployed.

Args:
    $1: whoami
"""

import sys

import requests

import secrets


HIPCHAT_API_URL = 'https://api.hipchat.com/v1/rooms/message'


def notify_hipchat(deployer, room_id):
    message = '%s just deployed to vimawesome.com' % deployer

    payload = {
        'auth_token': secrets.HIPCHAT_TOKEN,
        'notify': 0,
        'color': 'purple',
        'from': 'Mr Monkey',
        'room_id': room_id,
        'message': message,
        'message_format': 'text',
    }

    r = requests.post(HIPCHAT_API_URL, data=payload)
    print 'Message sent to HipChat: %s\nResponse: %s' % (message, r.text)


if __name__ == '__main__':
    deployer = sys.argv[1] if len(sys.argv) >= 2 else "vim-awesome server"

    notify_hipchat(deployer, secrets.HIPCHAT_ROOM_ID)
