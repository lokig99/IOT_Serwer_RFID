#!/usr/bin/env python3
# pylint: disable=no-member
import RPi.GPIO as GPIO

# ------------- config ---------------

# mqtt broker
__BROKER__ = 'localhost'

# ------------------------------------


def configInfo():
    print('This is only configuration file.\n')


if __name__ == "__main__":
    configInfo()
