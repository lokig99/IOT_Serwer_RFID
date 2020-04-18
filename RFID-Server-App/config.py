#!/usr/bin/env python3
# pylint: disable=no-member

# ------------- config ---------------

# mqtt broker
__BROKER__ = '127.0.0.1'  # (default is '127.0.0.1')

# server identifier
__SERVER_ID__ = 'server'  # (default is 'server')

# server broadcast interval (in seconds)
__BROADCAST_INTERVAL__ = 60  # (default is 60)

# print logs on exit
__SHOW_LOG_ON_EXIT__ = True  # (True/False)

# enable logging
__LOGGING_ENABLED__ = True  # (True/False)

# debug mode (show logs with level DEBUG)
__DEBUG_MODE__ = False  # (True/False)

# ------------------------------------


def configInfo():
    print('This is only configuration file.\n')


if __name__ == "__main__":
    configInfo()
