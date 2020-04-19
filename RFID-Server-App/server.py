#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import time
import logging
import data
import config
import threading
from datetime import datetime as date

# MQTT topics
__TERMINAL_DEBUG__ = 'terminal/debug'
__RFID_RECORD__ = 'rfid/record'
__SERVER_BROADCAST__ = 'server/broadcast'

__MQTT_TOPICS__ = [(__TERMINAL_DEBUG__, 0), (__RFID_RECORD__, 0)]

# path to whitelist file
__WHITE_LIST_PATH__ = './whitelist.txt'

# path to current session log
__SESSION_LOG_PATH__ = f"{date.now().strftime('%d-%m-%Y-%H-%M-%S')}.log"

# logger configuration
if config.__LOGGING_ENABLED__:
    if config.__DEBUG_MODE__:
        logLevel = logging.DEBUG
    else:
        logLevel = logging.INFO

    logging.basicConfig(filename=__SESSION_LOG_PATH__, filemode='w',
                        format='[%(asctime)s][%(levelname)s] %(message)s', level=logLevel, datefmt='%d-%m-%Y %H:%M:%S')
else:
    logging.disable(logging.CRITICAL)


def getSessionLogs():
    """
    Returns:\n
    \tlist(str) logs
    """
    logs = []
    if not os.path.exists(__SESSION_LOG_PATH__):
        return logs

    with open(__SESSION_LOG_PATH__, 'r') as logfile:
        lines = logfile.readlines()
        for line in lines:
            logs.append(line.strip('\n'))
        return logs


class NetworkScanner:
    def __init__(self):
        # The MQTT client.
        self.__client = mqtt.Client()
        self.__available_terminals = []
        self.__stop_broadcast = False
        self.__time_of_last_broadcast = []
        self.__broadcast_sender = threading.Thread(target=self.__broadcast_loop, args=(
            lambda: self.__stop_broadcast, self.__time_of_last_broadcast), daemon=True)

    def __str__(self):
        return self.__class__.__name__

    def __connect_to_broker(self):
        self.__client.connect(config.__BROKER__)
        self.__client.on_message = self.__process_broadcast
        self.__client.loop_start()
        self.__client.subscribe(__SERVER_BROADCAST__)
        logging.info(
            f'[{self}] connected to broker: {config.__BROKER__}')

    def __process_broadcast(self, client, userdata, message):
        message_decoded = (str(message.payload.decode('utf-8'))).split('.')

        if len(message_decoded) == 2:
            (terminal_id, server_id) = message_decoded
            if server_id == config.__SERVER_ID__:
                if not terminal_id in self.__available_terminals:
                    self.__available_terminals.append(terminal_id)
                    logging.info(
                        f'[{self}] terminal with id={terminal_id} found in network')

    def __broadcast_loop(self, stop, lastBroadcastTracker=[]):
        interval = config.__BROADCAST_INTERVAL__
        prev_broadcast = -interval

        while True:
            now = time.time()
            if now - prev_broadcast > interval:
                logging.debug(self.getAvailableTerminals())
                self.__available_terminals.clear()
                self.__client.publish(
                    __SERVER_BROADCAST__, config.__SERVER_ID__)
                prev_broadcast = now
                lastBroadcastTracker.clear()
                lastBroadcastTracker.append(now)
                logging.debug(lastBroadcastTracker)
                logging.info(f'[{self}] sent network broadcast')
            if stop():
                logging.info(f'[{self}] killing broadcast thread')
                break
            # update once every 500 ms to have mercy on the CPU
            time.sleep(0.5)

    def __disconnect_from_broker(self):
        self.__client.loop_stop()
        self.__client.disconnect()
        logging.info(
            f'[{self}] disconnected from broker: {config.__BROKER__}')

    def getAvailableTerminals(self):
        return self.__available_terminals[:]

    def getLastBroadcastTime(self):
        return self.__time_of_last_broadcast[0]

    def run(self):
        self.__connect_to_broker()
        self.__broadcast_sender.start()

    def stop(self):
        self.__disconnect_from_broker()
        self.__stop_broadcast = True
        self.__broadcast_sender.join()


class Server:
    def __init__(self, dataBase=data.EmployeesDataBase()):
        # The white-list of terminals (terminal IDs)
        self.__terminals_whitelist = []
        # The employees database
        self.__database = dataBase
        # The MQTT client.
        self.__server_client = mqtt.Client()
        # The network scanner
        self.__networkScanner = NetworkScanner()

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
                    logging.info(
                        '--- finished loading terminal-IDs from whitelist file ---')
        else:
            file = open(__WHITE_LIST_PATH__, 'w')
            file.close()
            logging.info('created "whitelist.txt" file')

    def __process_message(self, client, userdata, message):
        message_decoded = (str(message.payload.decode('utf-8'))).split('.')

        if message.topic == __TERMINAL_DEBUG__:
            logging.info(
                f'(Terminal-id: {message_decoded[1]}) {message_decoded[0]}')

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

    def getAvailableTerminals(self):
        return self.__networkScanner.getAvailableTerminals()

    def getLastBroadcastTime(self):
        return self.__networkScanner.getLastBroadcastTime()

    def getWhitelist(self):
        return self.__terminals_whitelist[:]

    def run(self):
        self.__connect_to_broker()
        self.__load_whitelist()
        self.__networkScanner.run()

    def stop(self):
        self.__disconnect_from_broker()
        self.__networkScanner.stop()


if __name__ == "__main__":
    server = Server()
    scanner = NetworkScanner()
    server.run()
    scanner.run()
    server.addTerminal('terminal')
    
    while True:
        inp = input('enter "q" to exit\n')
        if inp == 'q':
            break

    server.stop()
    scanner.stop()
    for log in getSessionLogs():
        print(log)
