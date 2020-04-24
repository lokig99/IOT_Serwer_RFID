#!/usr/bin/env python3
import src.data as data
import os
import time
import threading
import src.server as srv
from src.logger import *
from config import *
from operator import itemgetter

# The employees database
database = data.EmployeesDataBase()

# The MQTT server
server = srv.Server(database)

# The main loop bool value
__PROGRAM_STATUS__ = True

dataModified = [False]

__STOP_THREADS__ = False


def __autosave_loop(app_modified, database, server):
    interval = 30  # in seconds
    lastSave = time.time()

    while True:
        now = time.time()
        if now - lastSave > interval:
            if app_modified[0] or server.dataModified:
                logging.info('[Autosave] starting job')
                database.save()
                server.save_whitelist()
                app_modified[0] = False
                server.dataModified = False
            else:
                logging.info('[Autosave] no changes made -> skipping')
            lastSave = now
        time.sleep(1)


def clrScreen():
    os.system("cls" if os.name == "nt" else "clear")


def endMainLoop():
    global __PROGRAM_STATUS__
    print('exiting program...')
    __PROGRAM_STATUS__ = False


def _get_employees_summary_sorted():
    emp_data = database.getEmployeesDataSummary(includeHistory=False)
    emp_data.sort(key=itemgetter(1))
    emp_data.sort(key=lambda tup: tup[0] == tup[1])
    return emp_data


def _print_employees_list():
    emp_data = _get_employees_summary_sorted()

    if len(emp_data) > 0:
        max_name_len = max(list(map(len, [item[1] for item in emp_data])))

        for index, emp in enumerate(emp_data, 1):
            sep = '     '
            for i in range(max_name_len - len(emp[1])):
                sep += ' '

            print(f"[{index}] {emp[1]}", f"({emp[2]}, {emp[0]})", sep=sep)


def _selectOption(options=tuple(), on_except=None):
    try:
        option_num = int(input("\nEnter option number: "))
    except:
        if on_except != None:
            on_except()
        return

    for num, option in enumerate(options, 1):
        if num != option_num:
            continue
        option()
        break


def _selectList(positions, fun, *args, printList=True):
    if len(positions) > 0:
        if printList:
            for num, position in enumerate(positions, 1):
                print(f'[{num}] {position}')

        try:
            pos_num = int(input("\nEnter position number: ")) - 1
        except:
            return (None, None)

        if pos_num >= 0:
            if pos_num < len(positions):
                if fun != None:
                    res = fun(positions[pos_num], *args)
                    return (positions[pos_num], res)
                else:
                    return (positions[pos_num], None)

    return (None, None)


def mainMenu():
    clrScreen()
    print('MQTT Broker address:', BROKER,
          '\tServer ID:', SERVER_ID)
    print("\n--- Console RFID server Menu ---\n")
    print("[1] Manage terminals")
    print("[2] Manage employees")
    print("[3] Show server logs")
    print("[4] Stop server and quit")

    _selectOption(options=_mainMenuOptions)


def manageTerminalsMenu():
    clrScreen()
    print('(<-- main-menu)')
    print('\n--- Manage terminals ---\n')
    print("[1] Add terminal to whitelist")
    print("[2] Remove terminal from whitelist")
    print("[3] Show terminals on whitelist")
    print("[4] Show terminals available on network")
    print('[5] Return to main-menu')

    _selectOption(options=_manageTerminalsMenuOptions)


def manageEmployeesMenu():
    clrScreen()
    print('(<-- main-menu)')
    print('\n--- Manage employees ---\n')
    print("[1] Show list of all registered employees")
    print("[2] Add new employee to database")
    print("[3] Delete an employee from database")
    print("[4] Modify an employee's data")
    print("[5] Generate report for an employee")
    print('[6] Return to main-menu')

    _selectOption(options=_manageEmployeesMenuOptions)


def modifyEmpDataMenu():
    clrScreen()
    print('(<-- manage employees menu)')
    print("\n--- Modify an employee's data ---\n")
    print("[1] Change name")
    print("[2] Change RFID card")
    print('[3] Return to previous menu')

    _selectOption(options=_modifyEmpDataMenuOptions,
                  on_except=manageEmployeesMenu)


def showServerLogs():
    clrScreen()
    if LOGGING_ENABLED:
        for log in getSessionLogs():
            print(log)
    else:
        print('\t--- logging disabled ---')
    input('\n\n--- press enter to return to main-menu ---')


def addTerminal():
    clrScreen()
    print('(<-- manage terminals menu)')
    print('\n--- Add new terminal to white-list ---\n')
    terminal_id = input('Enter identifier of terminal you want to add:\n')
    if terminal_id.replace(' ', '').replace('-', 'a').replace('_', 'a').isalnum():
        if server.addTerminal(terminal_id):
            print(f'Added new terminal with id={terminal_id} to whitelist')
            dataModified[0] = True
        else:
            print(f'Terminal with id={terminal_id} is already on whitelist')

    input('\n\n--- press enter to return to previous menu ---')
    manageTerminalsMenu()


def removeTerminal():
    clrScreen()
    print('(<-- manage terminals menu)')
    print('\n--- Remove terminal from white-list ---\n')

    terminals = server.getWhitelist()
    if len(terminals) < 1:
        print('--- No terminals on whitelist ---')
    else:
        result = _selectList(terminals, server.removeTerminal)
        if result != (None, None):
            (terminal_id, res) = result
            if res:
                print(f'Removed terminal with id={terminal_id} from whitelist')
                dataModified[0] = True
        else:
            print(f'\n--- no terminal selected ---')

    input('\n\n--- press enter to return to previous menu ---')
    manageTerminalsMenu()


def showTerminalsNet():
    clrScreen()
    print('(<-- manage terminals menu)')
    print('\n--- Terminals on network ---\n')

    terminals = server.getAvailableTerminals()

    if len(terminals) > 0:
        id_len = list(map(len, terminals))

        for terminal_id in terminals:
            sep = '     '
            for i in range(max(id_len) - len(terminal_id)):
                sep += ' '

            print(terminal_id,
                  f'[on whitelist = {terminal_id in server.getWhitelist()}]', sep=sep)
    else:
        print('--- No terminals found in previous scan ---')
        print('Try again after next scan (server broadcast interval)')

    print(
        f'\n\nNext network scan in {BROADCAST_INTERVAL - round(time.time() - server.getLastBroadcastTime())} seconds from now')

    input('\n\n--- press enter to return to previous menu ---')
    manageTerminalsMenu()


def showTerminalsWhitelist():
    clrScreen()
    print('(<-- manage terminals menu)')
    print('\n--- Terminals on white-list ---\n')

    terminals = server.getWhitelist()

    if len(terminals) > 0:
        id_len = list(map(len, terminals))

        for terminal_id in terminals:
            sep = '     '
            for i in range(max(id_len) - len(terminal_id)):
                sep += ' '

            print(
                terminal_id, f'[isAvailable: {terminal_id in server.getAvailableTerminals()}]', sep=sep)
    else:
        print('--- No terminals on whitelist ---')

    print(
        f'\n\nNext network scan in {BROADCAST_INTERVAL - round(time.time() - server.getLastBroadcastTime())} seconds from now',
        '(isAvailable status)')

    input('\n\n--- press enter to return to previous menu ---')
    manageTerminalsMenu()


def showEmployees():
    clrScreen()
    print('(<-- manage employees menu)')
    print('\n--- Employees in database ---\n')

    _print_employees_list()

    input('\n\n--- press enter to return to previous menu ---')
    manageEmployeesMenu()


def addEmployee():
    clrScreen()
    print('(<-- manage employees menu)')
    print('\n--- Add Employee to database ---\n')

    emp_name = input('Enter name of the employee you want to add:\n')
    if emp_name.replace(' ', '').replace('-', 'a').replace('_', 'a').isalpha():
        while True:
            try:
                rfid_uid = int(input('Enter RFID card identifier:\n'))

            except:
                print('--- invalid input (RFID UID can only contain digits)---')
                continue
            break

        try:
            database.addEmployee(rfid_uid, name=emp_name)
            print(f'added new employee named {emp_name} to database')
            print(f'registered new RFID card with UID: {rfid_uid}')
            dataModified[0] = True
        except data.InvalidInputDataError:
            print('--- invalid input (check if name does not contain ";" signs)')
        except data.RfidAlreadyUsedError:
            print(
                f'given RFID UID is already used by the employee named {database.getEmpName(rfid_uid)}')

    input('\n\n--- press enter to return to previous menu ---')
    manageEmployeesMenu()


def removeEmployee():
    clrScreen()
    print('(<-- manage employees menu)')
    print('\n--- Remove an Employee from database ---\n')

    _print_employees_list()
    (emp_data, res) = _selectList(
        _get_employees_summary_sorted(), None, printList=False)
    if emp_data != None:
        rfid_uid = emp_data[2]
        try:
            database.deleteEmployee(rfid_uid)
            print(f'removed employee named {emp_data[1]} from database')
            print(f'unregistered RFID card with UID: {rfid_uid}')
            dataModified[0] = True
        except data.DataBaseError:
            print(f'--- uknown database error ---')

    input('\n\n--- press enter to return to previous menu ---')
    manageEmployeesMenu()


def generateReport():
    clrScreen()
    print('(<-- manage employees menu)')
    print('\n--- Generate report for an employee ---\n')

    _print_employees_list()
    (emp_data, res) = _selectList(
        _get_employees_summary_sorted(), None, printList=False)
    if emp_data != None:
        rfid_uid = emp_data[2]
        try:
            path = database.generateReport(rfid_uid)
            print('generated report')
            print(f'path to file: {os.path.abspath(path)}')
        except data.NoDataError:
            print(f'selected employee has no entries yet')

    input('\n\n--- press enter to return to previous menu ---')
    manageEmployeesMenu()


def modifyRFID():
    clrScreen()
    print('(<-- manage employees menu)')
    print('\n--- change employee\'s RFID card ---\n')

    _print_employees_list()
    (emp_data, res) = _selectList(
        _get_employees_summary_sorted(), None, printList=False)
    if emp_data != None:
        rfid_uid = emp_data[2]

        while True:
            try:
                new_rfid_uid = int(input('Enter new RFID card identifier:\n'))
            except:
                print('--- invalid input (RFID UID can only contain digits) ---')
                continue
            break

        try:
            database.modifyEmpRFID(rfid_uid, new_rfid_uid)
            print(
                f'{emp_data[1]}\'s RFID card updated with new UID: {new_rfid_uid}')
            print(f'unregistered RFID card with UID: {rfid_uid}')
            dataModified[0] = True
        except data.RfidAlreadyUsedError:
            print(
                f'given RFID card with UID: {new_rfid_uid} is already used by employee named {database.getEmpName(new_rfid_uid)}')
        except data.InvalidInputDataError:
            print('invalid input - RFID UID cannot be negative')

    input('\n\n--- press enter to return to previous menu ---')
    manageEmployeesMenu()


def modifyName():
    clrScreen()
    print('(<-- manage employees menu)')
    print('\n--- change employee\'s name ---\n')

    _print_employees_list()
    (emp_data, res) = _selectList(
        _get_employees_summary_sorted(), None, printList=False)
    if emp_data != None:
        rfid_uid = emp_data[2]

        emp_name = input('Enter new name for the employee:\n')
        if emp_name.replace(' ', '').replace('-', 'a').replace('_', 'a').isalpha():
            try:
                database.modifyEmpName(rfid_uid, emp_name)
                print(f'{emp_data[1]}\'s name changed to: {emp_name}')
                dataModified[0] = True
            except data.InvalidInputDataError:
                print('--- invalid input (check if name does not contain ";" signs)')

    input('\n\n--- press enter to return to previous menu ---')
    manageEmployeesMenu()


# The main-menu options
_mainMenuOptions = (manageTerminalsMenu, manageEmployeesMenu,
                    showServerLogs, endMainLoop)

# The manage terminals menu options
_manageTerminalsMenuOptions = (
    addTerminal, removeTerminal, showTerminalsWhitelist, showTerminalsNet, mainMenu)

# The manage employees menu options
_manageEmployeesMenuOptions = (
    showEmployees, addEmployee, removeEmployee, modifyEmpDataMenu, generateReport, mainMenu)

# The modify employee's data menu options
_modifyEmpDataMenuOptions = (modifyName, modifyRFID, manageEmployeesMenu)


def main():
    server.run()
    autosaver = threading.Thread(target=__autosave_loop, args=(
        dataModified, database, server), daemon=True)
    autosaver.start()

    while __PROGRAM_STATUS__:
        mainMenu()
    server.stop()
    logging.shutdown()
    database.save()

    clrScreen()
    if SHOW_LOG_ON_EXIT:
        for log in getSessionLogs():
            print(log)

if __name__ == "__main__":
    main()
