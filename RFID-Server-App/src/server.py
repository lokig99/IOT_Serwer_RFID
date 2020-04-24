#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import os
import time
import src.data as data
import threading
import json
from src.logger import *
from config import *
from src.constants import *
from datetime import datetime as date

# create DATA directory if doesn't exist already
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

# path to whitelist file
__WHITELIST_PATH__ = f'{DATA_DIR}/whitelist.json'

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
        self.__client.connect(BROKER)
        self.__client.on_message = self.__process_broadcast
        self.__client.loop_start()
        self.__client.subscribe(BROADCAST_REPLY)
        logging.info(
            f'[{self}] connected to broker: {BROKER}')

    def __process_broadcast(self, client, userdata, msg):
        msg_json = json.loads(msg.payload)
        terminal_id = msg_json[JSON_TERMINAL_ID]

        if SERVER_ID == msg_json[JSON_SERVER_ID]:
            if not terminal_id in self.__available_terminals:
                self.__available_terminals.append(terminal_id)
                logging.info(
                    f'[{self}] terminal with id={terminal_id} found in network')

    def __broadcast_loop(self, stop, lastBroadcastTracker=[]):
        interval = BROADCAST_INTERVAL
        prev_broadcast = -interval

        while True:
            now = time.time()
            if now - prev_broadcast > interval:
                logging.debug(self.getAvailableTerminals())
                self.__available_terminals.clear()

                msg = {JSON_SERVER_ID: SERVER_ID}
                msg_json = json.dumps(msg)

                self.__client.publish(
                    BROADCAST_REQUEST, msg_json)
                prev_broadcast = now
                lastBroadcastTracker.clear()
                lastBroadcastTracker.append(now)
                logging.debug(lastBroadcastTracker)
                logging.info(f'[{self}] sent network broadcast')
            if stop():
                logging.info(f'[{self}] killing broadcast thread')
                break
            # update once every second to have mercy on the CPU
            time.sleep(1)

    def __disconnect_from_broker(self):
        self.__client.loop_stop()
        self.__client.disconnect()
        logging.info(
            f'[{self}] disconnected from broker: {BROKER}')

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
  
        self.dataModified = False

    def __load_whitelist(self):
        if not os.path.exists(__WHITELIST_PATH__):
            self.__terminals_whitelist = []
            return

        with open(__WHITELIST_PATH__, 'r') as wlFile:
            logging.info(
                f'--- loading terminal-IDs from "{__WHITELIST_PATH__}" ---')
            self.__terminals_whitelist = json.load(wlFile)
            for terminal_id in self.__terminals_whitelist:
                logging.info(
                    f'added terminal with id={terminal_id} to terminal-whitelist')
            logging.info(
                '--- finished loading terminal-IDs from whitelist file ---')

    def save_whitelist(self):
        with open(__WHITELIST_PATH__, 'w') as wlFile:
            json.dump(self.__terminals_whitelist, wlFile, indent=4)
            logging.info('saved terminals whitelist')


    def __process_message(self, client, userdata, msg):
        msg_json = json.loads(msg.payload)

        if msg.topic == TERMINAL_DEBUG:
            logging.info(
                f'(Terminal-id: {msg_json[JSON_TERMINAL_ID]}) {msg_json[JSON_TEXT]}')

        elif msg.topic == RFID_RECORD and msg_json[JSON_TERMINAL_ID] in self.__terminals_whitelist:
            (day, month, year, hour,
             minute) = [int(item) for item in msg_json[JSON_RFID_DATE].split('.')]
            terminal_id = msg_json[JSON_TERMINAL_ID]
            rfid_uid = msg_json[JSON_RFID_UID]

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
            self.dataModified = True

    def __connect_to_broker(self):
        self.__server_client.connect(BROKER)
        self.__server_client.on_message = self.__process_message
        self.__server_client.loop_start()
        self.__server_client.subscribe([(RFID_RECORD, 0), (TERMINAL_DEBUG, 0)])
        logging.info(f'connected to broker: {BROKER}')

    def __disconnect_from_broker(self):
        self.__server_client.loop_stop()
        self.__server_client.disconnect()
        logging.info(f'disconnected from broker: {BROKER}')

    def addTerminal(self, terminal_id):
        if terminal_id in self.__terminals_whitelist:
            logging.error(
                f'addTerminal - terminal with id={terminal_id} is already listed in whitelist')
            return False
        else:
            self.__terminals_whitelist.append(terminal_id)
            logging.info(
                f'addTerminal - terminal with id={terminal_id} added to whitelist')

            self.dataModified = True
        return True

    def removeTerminal(self, terminal_id):
        if not terminal_id in self.__terminals_whitelist:
            logging.error(
                f'removeTerminal - no terminal with id={terminal_id} in whitelist')
            return False
        else:
            self.__terminals_whitelist.remove(terminal_id)
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
        self.save_whitelist()