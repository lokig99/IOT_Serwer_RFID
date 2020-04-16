#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import time
import logging
import data
import config
import keyboard
from datetime import datetime as date

# MQTT topics
__TERMINAL_DEBUG__ = 'terminal/debug'
__SERVER_PING__ = 'server/ping'
__TERMINAL_PING__ = 'terminal/ping'
__RFID_RECORD__ = 'rfid/record'

__MQTT_TOPICS__ = [(__TERMINAL_DEBUG__, 0), (__SERVER_PING__, 0),
                   (__TERMINAL_PING__, 0), (__RFID_RECORD__, 0)]

# ping consts
__PING_RESPONSE__ = 1
__PING_CALL__ = 0

# path to whitelist file
__WHITE_LIST_PATH__ = './whitelist.txt'

# path of log directory
__LOGS_DIR__ = "./logs/"

# path to current session log
__SESSION_LOG_PATH__ = f"{__LOGS_DIR__}{date.now().strftime('%d-%m-%Y-%H-%M-%S')}.log"

# logger configuration
if not os.path.exists(__LOGS_DIR__):
    os.mkdir(__LOGS_DIR__)
logging.basicConfig(filename=__SESSION_LOG_PATH__, filemode='w',
                    format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.DEBUG, datefmt='%d-%m-%Y %H:%M:%S')


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


class Server:
    def __init__(self, dataBase=data.EmployeesDataBase()):
        # The white-list of terminals (terminal IDs)
        self.__terminals_whitelist = []
        # The employees database
        self.__database = dataBase
        # The MQTT client.
        self.__server_client = mqtt.Client()

    def __load_whitelist(self):
        if os.path.exists(__WHITE_LIST_PATH__):
            if os.stat(__WHITE_LIST_PATH__).st_size > 0:
                with open(__WHITE_LIST_PATH__, 'r') as file:
                    lines = map(lambda string: string.strip(
                        '\n'), file.readlines())
                    logging.info(
                        '--- loading terminal-IDs from whitelist file ---')
                    for line in lines:
                        self.__terminals_whitelist.append(line)
                        logging.info(
                            f'added terminal with id={line} to terminal-whitelist')
                        self.__ping_terminal(line)
                    logging.info(
                        '--- finished loading terminal-IDs from whitelist file ---')
        else:
            file = open(__WHITE_LIST_PATH__, 'w')
            file.close()
            logging.info('created "whitelist.txt" file')

    def __ping_terminal(self, terminal_id, status=__PING_CALL__):
        self.__server_client.publish(__SERVER_PING__, f'{terminal_id}.{config.__SERVER_ID__}.{status}')
        logging.info(
            f'published ping message - target terminal_id: {terminal_id}')

    def __process_message(self, client, userdata, message):
        message_decoded = (str(message.payload.decode('utf-8'))).split('.')

        if message.topic == __TERMINAL_DEBUG__:
            logging.info(
                f'(Terminal-id: {message_decoded[1]}) {message_decoded[0]}')

        elif message.topic == __TERMINAL_PING__:
            (terminal_id, server_id, ping_status) = message_decoded
            if server_id == config.__SERVER_ID__:
                if int(ping_status) == __PING_CALL__:
                    self.__ping_terminal(terminal_id, __PING_RESPONSE__)
                else:
                    logging.info(f'received ping response from terminal with id: {terminal_id}')

        elif message.topic == __RFID_RECORD__ and message_decoded[-1] in self.__terminals_whitelist:
            (rfid_uid, day, month, year, hour, minute) = [
                int(item) for item in message_decoded[:-1]]
            terminal_id = message_decoded[-1]

            logging.info(
                f'(Terminal-id: {terminal_id}) RFID scanned: {rfid_uid}')

            try:
                self.__database.addEntry(rfid_uid, rfid_terminal=terminal_id,
                                         date=date(year, month, day, hour, minute))
                logging.info(
                    f'added entry for employee named {self.__database.getEmpName(rfid_uid)} (rfid_uid={rfid_uid})')
            except data.NoSuchEmployeeError:
                logging.warning(
                    f'No such employee with rfid_uid={rfid_uid} in database')
                self.__database.addEmployee(rfid_uid)
                logging.info(
                    f'added anonymous employee with rfid-uid={rfid_uid} to database')
                self.__database.addEntry(rfid_uid, rfid_terminal=terminal_id,
                                         date=date(year, month, day, hour, minute))
                logging.info(
                    f'added entry for employee named {self.__database.getEmpName(rfid_uid)} (rfid_uid={rfid_uid})')
            except:
                logging.exception('unknown exception')

    def __connect_to_broker(self):
        self.__server_client.connect(config.__BROKER__)
        self.__server_client.on_message = self.__process_message
        self.__server_client.loop_start()
        self.__server_client.subscribe(__MQTT_TOPICS__)
        logging.info(f'connected to broker: {config.__BROKER__}')

    def __disconnect_from_broker(self):
        self.__server_client.loop_stop()
        self.__server_client.disconnect()
        logging.info(f'disconnected from broker: {config.__BROKER__}')

    def addTerminal(self, terminal_id):
        if terminal_id in self.__terminals_whitelist:
            logging.error(
                f'addTerminal - terminal with id={terminal_id} is already listed in whitelist')
            return False
        else:
            self.__terminals_whitelist.append(terminal_id)
            with open(__WHITE_LIST_PATH__, 'a') as whitelist:
                whitelist.write(terminal_id + '\n')

            logging.info(
                f'addTerminal - terminal with id={terminal_id} added to whitelist')
        return True

    def removeTerminal(self, terminal_id):
        if not terminal_id in self.__terminals_whitelist:
            logging.error(
                f'removeTerminal - no terminal with id={terminal_id} in whitelist')
            return False
        else:
            self.__terminals_whitelist.remove(terminal_id)
            with open(__WHITE_LIST_PATH__, 'r') as file:
                lines = map(lambda string: string.strip(
                    '\n'), file.readlines())
            with open(__WHITE_LIST_PATH__, 'w') as file:
                for line in lines:
                    if line != terminal_id:
                        file.write(line + '\n')
            logging.info(
                f'removeTerminal - terminal with id={terminal_id} removed from whitelist')
        return True

    def run(self):
        self.__connect_to_broker()
        self.__load_whitelist()

    def stop(self):
        self.__disconnect_from_broker()


if __name__ == "__main__":
    server = Server()
    server.run()
    server.addTerminal('terminal')
    while not keyboard.is_pressed('q'):
        pass
    server.stop()
    for log in getSessionLogs():
        print(log)
