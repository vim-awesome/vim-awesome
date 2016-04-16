"""Sends a message to Gitter that we just deployed.

Args:
    $1: whoami
"""

import sys
from util import log_to_gitter


def notify_gitter(deployer):
    message = '%s just deployed to vimawesome.com' % deployer
    log_to_gitter(message)
    print 'Message sent to Gitter: %s' % message


if __name__ == '__main__':
    deployer = sys.argv[1] if len(sys.argv) >= 2 else "vim-awesome server"

    notify_gitter(deployer)
