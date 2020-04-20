#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import sys
import time
import logging
from config import *
import keyboard
import rfid
import json
import threading
from mqttConstans import *
from zipfile import ZipFile, ZIP_BZIP2
from datetime import datetime as date


# The MQTT client.
client = mqtt.Client()

# path to current session log
__SESSION_LOG_PATH__ = f"{date.now().strftime('%d-%m-%Y-%H-%M-%S')}.log"

# logger configuration
logFormatter = logging.Formatter(
    '[%(asctime)s][%(levelname)s] %(message)s', '%d-%m-%Y %H:%M:%S')
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(__SESSION_LOG_PATH__, 'w')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

logging.debug('logger configured correctly')


def __call_server(topic, msg_json):
    client.publish(topic, msg_json)
    logging.info(
        f'sent MQTT message: [{topic}] {msg_json}')


def __process_message(client, userdata, msg):
    msg_json = json.loads(msg.payload)

    if msg.topic == BROADCAST_REQUEST:
        logging.info(
            f'received broadcast msg from server with id={msg_json[JSON_SERVER_ID]}')
        reply = json.dumps({JSON_TERMINAL_ID: TERMINAL_ID,
                            JSON_SERVER_ID: msg_json[JSON_SERVER_ID]})
        __call_server(BROADCAST_REPLY, reply)


def __connect_to_broker():
    client.connect(BROKER)
    client.on_message = __process_message
    client.loop_start()
    client.subscribe(BROADCAST_REQUEST)
    logging.info(f'connected to broker: {BROKER}')

    msg_json = json.dumps(
        {JSON_TERMINAL_ID: TERMINAL_ID, JSON_TEXT: 'Client connected'})
    __call_server(TERMINAL_DEBUG, msg_json)


def __disconnect_from_broker():
    msg_json = json.dumps(
        {JSON_TERMINAL_ID: TERMINAL_ID, JSON_TEXT: 'Client disconnected'})
    __call_server(TERMINAL_DEBUG, msg_json)
    logging.info(f'disconnected from broker: {BROKER}')
    client.disconnect()
    client.loop_stop()


def __rfid_scan_loop(terminal_id):
    prev_rfid_uid = -1

    while True:
        rfid_uid = rfid.rfidRead()
        if rfid_uid != -1:
            if prev_rfid_uid != rfid_uid:
                prev_rfid_uid = rfid_uid
                msg_json = json.dumps({JSON_RFID_UID: rfid_uid, JSON_TERMINAL_ID: TERMINAL_ID,
                                       JSON_RFID_DATE: date.now().strftime("%d.%m.%Y.%H.%M")})
                __call_server(
                    RFID_RECORD, msg_json)
        else:
            prev_rfid_uid = -1

        time.sleep(0.01)  # update once every 10 ms to have mercy on the CPU


def run():
    __connect_to_broker()
    rfid_scanner = threading.Thread(target=__rfid_scan_loop, args=(
        TERMINAL_ID, ), daemon=True)
    rfid_scanner.start()


if __name__ == "__main__":
    run()
    while True:
        inp = input('\nenter "stop" to exit\n')
        if inp.lower() == 'stop':
            break

    __disconnect_from_broker()
    logging.info('shutting down terminal...')
    logging.shutdown()

    if not os.path.exists('logs.zip'):
        with ZipFile('logs.zip', 'w', ZIP_BZIP2) as ziplog:
            ziplog.write(__SESSION_LOG_PATH__)
    else:
        with ZipFile('logs.zip', 'a', ZIP_BZIP2) as ziplog:
            ziplog.write(__SESSION_LOG_PATH__)

    os.remove(__SESSION_LOG_PATH__)
