#!/usr/bin/env python3
import datetime
import os
from random import randrange

__DATA_DIR_PATH__ = "data/"
__EMP_HISTORY_DIR_PATH__ = f"{__DATA_DIR_PATH__}emp_history/"
__DATA_EXTENSION__ = ".data"
__REPORT_EXTENSION__ = ".csv"
__EMPLOYEES_FILE_PATH__ = f"{__DATA_DIR_PATH__}employees{__DATA_EXTENSION__}"
__REPORT_DIR_PATH__ = "reports/"

### dictionaries ###
emp_hist_dict = {}
name_emp_dict = {}
emp_name_dict = {}
rfid_emp_dict = {}
emp_rfid_dict = {}
####################

#### exceptions ####

class EmployeeRecordAlreadyExistsError(Exception):
    pass


class NoSuchEmployeeError(Exception):
    pass


class NoDataError(Exception):
    pass

####################


def generateKey(length):
    if length <= 0:
        return None

    key = ""
    for i in range(length):
        # = 10 digits + 2*26 basic latin letter (lowercase & uppercase)
        randNumber = randrange(0, 62)
        if randNumber < 10:
            key += chr(randNumber + 48)  # digits
        elif randNumber >= 10 and randNumber < 36:
            key += chr(randNumber + 55)  # uppercase letters
        else:
            key += chr(randNumber + 61)  # lowercase letters
    return key


def addEntry(employee_uid, rfid_terminal=1, date=datetime.datetime.now()):
    if employee_uid not in emp_name_dict.keys():
        raise NoSuchEmployeeError

    filePath = f"{__EMP_HISTORY_DIR_PATH__}{employee_uid}{__DATA_EXTENSION__}"
    if os.path.exists(filePath):
        file = open(filePath, "a")
    else:
        file = open(filePath, "w")

    entryText = f"{date.day};{date.month};{date.year};{date.hour};{date.minute};{rfid_terminal}\n"
    file.write(entryText)
    file.close()

    # update emp_history dictionary
    emp_hist_dict[employee_uid].append(
        tuple([int(item) for item in entryText.split(';')]))


def clearDictionaries():
    emp_hist_dict.clear()
    emp_rfid_dict.clear()
    name_emp_dict.clear()
    emp_name_dict.clear()
    rfid_emp_dict.clear()


def reloadData():
    if not os.path.exists(__DATA_DIR_PATH__):
        os.mkdir(__DATA_DIR_PATH__)

    if not os.path.exists(__EMP_HISTORY_DIR_PATH__):
        os.mkdir(__EMP_HISTORY_DIR_PATH__)

    if not os.path.exists(__EMPLOYEES_FILE_PATH__):
        open(__EMPLOYEES_FILE_PATH__, "w")

    if os.stat(__EMPLOYEES_FILE_PATH__).st_size == 0:
        return

    clearDictionaries()
    # create name_emp and rfid_emp dictionary entries
    with open(__EMPLOYEES_FILE_PATH__, "r") as file:
        line = file.readline()
        while line != "":
            (emp_uid, name, rfid_uid) = line.split(';')
            name_emp_dict[name] = emp_uid
            emp_name_dict[emp_uid] = name
            rfid_emp_dict[int(rfid_uid)] = emp_uid
            emp_rfid_dict[emp_uid] = int(rfid_uid)
            line = file.readline()

    # create emp_history dictionary
    for emp_uid in emp_name_dict.keys():
        emp_hist_dict[emp_uid] = []

    # add entries to emp_history dictionary
    for emp_uid in emp_hist_dict.keys():
        filePath = f"{__EMP_HISTORY_DIR_PATH__}{emp_uid}{__DATA_EXTENSION__}"
        if os.path.exists(filePath):
            with open(filePath, "r") as file:
                line = file.readline()
                while line != "":
                    entry = tuple([int(item) for item in line.split(';')])
                    emp_hist_dict[emp_uid].append(entry)
                    line = file.readline()


def addEmployee(emp_uid, name, rfid_uid):
    if emp_uid in emp_name_dict.keys():
        raise EmployeeRecordAlreadyExistsError

    if os.path.exists(__EMPLOYEES_FILE_PATH__):
        file = open(__EMPLOYEES_FILE_PATH__, "a")
    else:
        file = open(__EMPLOYEES_FILE_PATH__, "w")

    file.write(f"{emp_uid};{name};{rfid_uid}\n")
    file.close()
    reloadData()


def deleteEmployee(emp_uid, delHistory=True):
    if emp_uid not in emp_name_dict.keys():
        raise NoSuchEmployeeError

    if os.path.exists(__EMPLOYEES_FILE_PATH__):
        with open(__EMPLOYEES_FILE_PATH__, "r") as file:
            lines = file.readlines()
        with open(__EMPLOYEES_FILE_PATH__, "w") as file:
            for line in lines:
                if line.split(';')[0] != str(emp_uid):
                    file.write(line)
    else:
        return

    # delete history file
    if delHistory:
        filePath = f"{__EMP_HISTORY_DIR_PATH__}{emp_uid}{__DATA_EXTENSION__}"
        if os.path.exists(filePath):
            os.remove(filePath)
    reloadData()


def modifyEmpName(emp_uid, newName):
    if emp_uid not in emp_name_dict.keys():
        raise NoSuchEmployeeError

    if os.path.exists(__EMPLOYEES_FILE_PATH__):
        with open(__EMPLOYEES_FILE_PATH__, "r") as file:
            lines = file.readlines()
            for line in lines:
                (uid, name, rfid_uid) = line.split(';')
                if uid == emp_uid:
                    rfid_uid = rfid_uid.strip('\n')
                    break
        deleteEmployee(uid, delHistory=False)
        addEmployee(uid, newName, rfid_uid)


def modifyEmpRFID(emp_uid, new_rfid_uid):
    if emp_uid not in emp_name_dict.keys():
        raise NoSuchEmployeeError

    if os.path.exists(__EMPLOYEES_FILE_PATH__):
        with open(__EMPLOYEES_FILE_PATH__, "r") as file:
            lines = file.readlines()
            for line in lines:
                (uid, name, rfid_uid) = line.split(';')
                if uid == emp_uid:
                    break
        deleteEmployee(uid, delHistory=False)
        addEmployee(uid, name, new_rfid_uid)


def generateReport(emp_uid):
    if emp_uid not in emp_name_dict.keys():
        raise NoSuchEmployeeError

    if len(emp_hist_dict[emp_uid]) == 0:
        raise NoDataError

    if not os.path.exists(__REPORT_DIR_PATH__):
        os.mkdir(__REPORT_DIR_PATH__)

    workDays = []  # date of entrance, date of leave, delta_time
    isWorkEntrace = True
    (day, month, year, hour, minute, terminal) = emp_hist_dict[emp_uid][0]
    prevDate = datetime.datetime(year, month, day, hour, minute)
    for entry in emp_hist_dict[emp_uid][1:]:
        isWorkEntrace = not isWorkEntrace
        (day, month, year, hour, minute, terminal) = entry
        if isWorkEntrace:
            prevDate = datetime.datetime(year, month, day, hour, minute)
        else:
            currentDate = datetime.datetime(year, month, day, hour, minute)
            workDays.append((prevDate, currentDate, (currentDate - prevDate)))

    filePath = f"{__REPORT_DIR_PATH__}" \
        f"{emp_name_dict[emp_uid].replace(' ', '_')}_" \
        f"{datetime.datetime.now().strftime('%b-%d-%Y-%H-%M-%S')}" \
        f"{__REPORT_EXTENSION__}"

    with open(filePath, "w") as file:
        for workDay in workDays:
            file.write(
                f"{workDay[0].strftime('%d/%m/%Y')};{workDay[1].strftime('%d/%m/%Y')};{workDay[2].total_seconds()}\n")
    return filePath


def test():
    #addEmployee("eeee", "Ryszard Samosia", 999)
    #addEmployee("aaaa", "Adam Abacki", 403)
    reloadData()
    # addEntry("cccc")
    #generateReport("cccc")
    print(emp_name_dict)
    print(name_emp_dict)
    print(emp_rfid_dict)
    print(rfid_emp_dict)
    print(emp_hist_dict)


if __name__ == "__main__":
    test()
