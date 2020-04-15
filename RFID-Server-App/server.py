#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import time
import logging
import data
import config
import keyboard
from datetime import datetime as date

# The employees database
database = data.EmployeesDataBase()

# MQTT topics
__TERMINAL_DEBUG__ = 'terminal/debug'
__RFID_RECORD__ = 'rfid/record'

# The white-list of terminals (terminal IDs)
terminals_whitelist = []

# path to whitelist file
__WHITE_LIST_PATH__ = './whitelist.txt'

# The MQTT client.
server_client = mqtt.Client()

# path of log directory
__LOGS_DIR__ = "./logs/"

# path to current session log
__SESSION_LOG_PATH__ = f"{__LOGS_DIR__}{date.now().strftime('%d-%m-%Y-%H-%M-%S')}.log"

# logger configuration
if not os.path.exists(__LOGS_DIR__):
    os.mkdir(__LOGS_DIR__)
logging.basicConfig(filename=__SESSION_LOG_PATH__, filemode='w',
                    format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.DEBUG, datefmt='%d-%m-%Y %H:%M:%S')
logging.debug('logger configured correctly')


def getSessionLogs():
    """
    Returns:\n
    \tlist(str) logs
    """
    logs = []
    if not os.path.exists(__LOGS_DIR__):
        return logs

    with open(__SESSION_LOG_PATH__, 'r') as logfile:
        lines = logfile.readlines()
        for line in lines:
            logs.append(line.strip('\n'))
        return logs


def __load_whitelist():
    if os.path.exists(__WHITE_LIST_PATH__):
        with open(__WHITE_LIST_PATH__, 'r') as file:
            lines = map(lambda string: string.strip('\n'), file.readlines())
            for line in lines:
                terminals_whitelist.append(line)
    else:
        file = open(__SESSION_LOG_PATH__, 'w')
        file.close()


def __process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode('utf-8'))).split('.')

    if message.topic == __TERMINAL_DEBUG__:
        logging.info(
            f'(Terminal-id: {message_decoded[1]}) {message_decoded[0]}')

    elif message.topic == __RFID_RECORD__ and message_decoded[-1] in terminals_whitelist:
        (rfid_uid, day, month, year, hour, minute) = [
            int(item) for item in message_decoded[:-1]]
        terminal_id = message_decoded[-1]

        logging.info(
            f'(Terminal-id: {terminal_id}) RFID scanned: {rfid_uid}')

        try:
            database.addEntry(rfid_uid, rfid_terminal=terminal_id,
                              date=date(year, month, day, hour, minute))
            logging.info(
                f'added entry for employee named {database.getEmpName(rfid_uid)} (rfid_uid={rfid_uid})')
        except data.NoSuchEmployeeError:
            logging.warning(
                f'No such employee with rfid_uid={rfid_uid} in database')
            database.addEmployee(rfid_uid)
            logging.info(
                f'added anonymous employee with rfid-uid={rfid_uid} to database')
            database.addEntry(rfid_uid, rfid_terminal=terminal_id,
                              date=date(year, month, day, hour, minute))
            logging.info(
                f'added entry for employee named {database.getEmpName(rfid_uid)} (rfid_uid={rfid_uid})')
        except:
            logging.exception('unknown exception')


def __connect_to_broker():
    server_client.connect(config.__BROKER__)
    server_client.on_message = __process_message
    server_client.loop_start()
    server_client.subscribe([(__TERMINAL_DEBUG__, 0), (__RFID_RECORD__, 0)])
    logging.info(f'connected to broker: {config.__BROKER__}')


def __disconnect_from_broker():
    server_client.loop_stop()
    server_client.disconnect()
    logging.info(f'disconnected from broker: {config.__BROKER__}')


def addTerminal(terminal_id):
    if terminal_id in terminals_whitelist:
        logging.error(
            f'addTerminal - terminal with id={terminal_id} is already listed in whitelist')
        return False
    else:
        terminals_whitelist.append(terminal_id)
        with open(__WHITE_LIST_PATH__, 'a') as whitelist:
            whitelist.write(terminal_id + '\n')

        logging.info(
            f'addTerminal - terminal with id={terminal_id} added to whitelist')
    return True


def removeTerminal(terminal_id):
    if not terminal_id in terminals_whitelist:
        logging.error(
            f'removeTerminal - no terminal with id={terminal_id} in whitelist')
        return False
    else:
        terminals_whitelist.remove(terminal_id)
        with open(__WHITE_LIST_PATH__, 'r') as file:
            lines = map(lambda string: string.strip('\n'), file.readlines())
        with open(__WHITE_LIST_PATH__, 'w') as file:
            for line in lines:
                if line != terminal_id:
                    file.write(line + '\n')
        logging.info(
            f'removeTerminal - terminal with id={terminal_id} removed from whitelist')
    return True


def run():
    __load_whitelist()
    __connect_to_broker()


def stop():
    __disconnect_from_broker()


if __name__ == "__main__":
    run()
    addTerminal('terminal')
    while not keyboard.is_pressed('Q'):
        pass
    stop()
