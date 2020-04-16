#!/usr/bin/env python3
# pylint: disable=no-member
import RPi.GPIO as GPIO

# ------------- config ---------------

# mqtt broker
__BROKER__ = '127.0.0.1'

# server identificator
__SERVER_ID__ = 'server'

# ------------------------------------


def configInfo():
    print('This is only configuration file.\n')


if __name__ == "__main__":
    configInfo()
