#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import sys
import time
import logging
import config
import keyboard
import rfid
import threading
from datetime import datetime as date


# The MQTT client.
client = mqtt.Client()

# MQTT topics
__TERMINAL_DEBUG__ = 'terminal/debug'
__SERVER_PING__ = 'server/ping'
__TERMINAL_PING__ = 'terminal/ping'
__RFID_RECORD__ = 'rfid/record'
__SERVER_BROADCAST__ = 'server/broadcast'

__MQTT_TOPICS__ = [(__TERMINAL_DEBUG__, 0), (__SERVER_PING__, 0),
                   (__TERMINAL_PING__, 0), (__RFID_RECORD__, 0)]

# ping consts
__PING_RESPONSE__ = 1
__PING_CALL__ = 0

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


def __process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode('utf-8'))).split('.')

    if message.topic == __SERVER_PING__:
        (terminal_id, server_id, ping_status) = message_decoded
        if terminal_id == config.__TERMINAL_ID__:
            if int(ping_status) == __PING_CALL__:
                __ping_server(server_id, __PING_RESPONSE__)
            else:
                logging.info(
                    f'received ping response from server with id: {server_id}')
    
    elif message.topic == __SERVER_BROADCAST__:
        if len(message_decoded) == 1:
            server_id = message_decoded[0]
            logging.info(f'received broadcast msg from server with id={server_id}')
            client.publish(__SERVER_BROADCAST__, f'{config.__TERMINAL_ID__}.{server_id}')


def __ping_server(server_id, status=__PING_CALL__):
    client.publish(__TERMINAL_PING__, f'{config.__TERMINAL_ID__}.{server_id}.{status}')
    logging.info(
        f'published ping message - target server_id: {server_id}')


def __connect_to_broker():
    client.connect(config.__BROKER__)
    client.on_message = __process_message
    client.loop_start()
    client.subscribe([(__SERVER_PING__, 0), (__SERVER_BROADCAST__, 0)])
    logging.info(f'connected to broker: {config.__BROKER__}')
    __call_server(__TERMINAL_DEBUG__, 'Client connected',
                  config.__TERMINAL_ID__)


def __disconnect_from_broker():
    __call_server(__TERMINAL_DEBUG__, 'Client disconnected',
                  config.__TERMINAL_ID__)
    logging.info(f'disconnected from broker: {config.__BROKER__}')
    client.disconnect()
    client.loop_stop()


def __rfid_scan_loop(terminal_id):
    prev_rfid_uid = -1

    while True:
        rfid_uid = rfid.rfidRead()
        if rfid_uid != -1:
            if prev_rfid_uid != rfid_uid:
                prev_rfid_uid = rfid_uid
                __call_server(
                    __RFID_RECORD__, f'{rfid_uid}.{date.now().strftime("%d.%m.%Y.%H.%M")}', config.__TERMINAL_ID__)
        else:
            prev_rfid_uid = -1

        time.sleep(0.1) #update once every 100 ms to have mercy on the CPU


def run():
    __connect_to_broker()
    rfid_scanner = threading.Thread(target=__rfid_scan_loop, args=(config.__TERMINAL_ID__, ), daemon=True )
    rfid_scanner.start()


if __name__ == "__main__":
    run()
    while not keyboard.is_pressed('ctrl + q'):
         time.sleep(0.01) #update once every 10 ms to have mercy on the CPU
    __disconnect_from_broker()
    logging.info('shutting down terminal...')
    #os.system('cls' if os.name == 'nt' else 'clear')
