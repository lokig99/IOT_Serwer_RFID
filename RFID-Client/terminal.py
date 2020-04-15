#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import sys
import time
import logging
import config
import keyboard
import rfid
from datetime import datetime as date


# The MQTT client.
client = mqtt.Client()

# MQTT topics
__TERMINAL_DEBUG__ = 'terminal/debug'
__RFID_RECORD__ = 'rfid/record'

# path of log directory
__LOGS_DIR__ = "./logs/"

# path to current session log
__SESSION_LOG_PATH__ = f"{__LOGS_DIR__}{date.now().strftime('%d-%m-%Y-%H-%M-%S')}.log"

# logger configuration
logFormatter = logging.Formatter(
    '[%(asctime)s][%(levelname)s] %(message)s', '%d-%m-%Y %H:%M:%S')
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

if not os.path.exists(__LOGS_DIR__):
    os.mkdir(__LOGS_DIR__)
fileHandler = logging.FileHandler(__SESSION_LOG_PATH__, 'w')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

logging.debug('logger configured correctly')


def __call_server(topic, message, terminal_id):
    client.publish(topic, message + '.' + terminal_id)
    logging.info(
        f'sent MQTT message: [{topic}] {message}.{terminal_id}')


def __connect_to_broker():
    client.connect(config.__BROKER__)
    logging.info(f'connected to broker: {config.__BROKER__}')
    __call_server(__TERMINAL_DEBUG__, 'Client connected', config.__TERMINAL_ID__)

def __disconnect_from_broker():
    __call_server(__TERMINAL_DEBUG__, 'Client disconnected', config.__TERMINAL_ID__)
    logging.info(f'disconnected from broker: {config.__BROKER__}')
    client.disconnect()


def __rfid_scan_loop(terminal_id):
    prev_rfid_uid = -1

    while True:
        if keyboard.is_pressed('ctrl + Q'):
            return
        rfid_uid = rfid.rfidRead()
        if rfid_uid != -1:
            if prev_rfid_uid != rfid_uid:
                prev_rfid_uid = rfid_uid
                __call_server(__RFID_RECORD__, f'{rfid_uid}.{date.now().strftime("%d.%m.%Y.%H.%M")}', config.__TERMINAL_ID__)
        else:
            prev_rfid_uid = -1
        
def run():
    __connect_to_broker()
    __rfid_scan_loop(config.__TERMINAL_ID__)
    
if __name__ == "__main__":
    run()
    __disconnect_from_broker()
    logging.info('shutting down terminal...')
    os.system('cls' if os.name == 'nt' else 'clear')
