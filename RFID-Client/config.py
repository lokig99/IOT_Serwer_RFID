#!/usr/bin/env python3
# pylint: disable=no-member
import RPi.GPIO as GPIO

# ------------- config ---------------

# terminal's mqtt identificator
__TERMINAL_ID__ = 'terminal'

# mqqt broker
__BROKER__ = 'localhost'

# ------------------------------------

def configInfo():
    print('This is only configuration file.\n')


if __name__ == "__main__":
    configInfo()
