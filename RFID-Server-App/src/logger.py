#!/usr/bin/env python3
from config import *
from datetime import datetime as date
from zipfile import ZipFile, ZIP_BZIP2
from src.utils import cd
import time
import logging
import os
import bz2

# path to current session log
__LOGS_DIR__ = "./logs"
__LOG_FILE__ = "latest.log"

# create logs dir
if not os.path.exists(__LOGS_DIR__):
    os.mkdir(__LOGS_DIR__)

# move old log to zip archive
with cd(__LOGS_DIR__):
    if os.path.exists(__LOG_FILE__):
        old_log_file = time.strftime(
            '%d-%m-%Y-%H-%M-%S.log', time.localtime(os.path.getctime(__LOG_FILE__)))
        os.rename(__LOG_FILE__, old_log_file)

        with ZipFile(old_log_file.replace('.log', '.zip'), 'w', ZIP_BZIP2) as ziplog:
            ziplog.write(old_log_file)

        os.remove(old_log_file)

# logger configuration
if LOGGING_ENABLED:
    if DEBUG_MODE:
        logLevel = logging.DEBUG
    else:
        logLevel = logging.INFO

    logging.basicConfig(filename=f'{__LOGS_DIR__}/{__LOG_FILE__}', filemode='w',
                        format='[%(asctime)s][%(levelname)s] %(message)s', level=logLevel, datefmt='%d-%m-%Y %H:%M:%S')
else:
    logging.disable(logging.CRITICAL)


def getSessionLogs():
    """
    Returns:\n
    \tlist(str) logs
    """
    logs = []
    with cd(__LOGS_DIR__):
        if os.path.exists(__LOG_FILE__):
            with open(__LOG_FILE__, 'r') as logfile:
                lines = logfile.readlines()
                for line in lines:
                    logs.append(line.strip('\n'))
    return logs