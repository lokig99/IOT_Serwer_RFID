#!/usr/bin/env python3
import datetime
import os
import threading
import pickle
from random import randrange
from src.constants import DATA_DIR

# create DATA directory if doesn't exist already
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

__DATA_FILEPATH__ = f"{DATA_DIR}/database.pkl"
__REPORT_EXTENSION__ = ".csv"
__REPORT_DIR_PATH__ = "./reports/"
__DEFAULT_KEY_LEN__ = 4


def generateKey(length):
    if length <= 0:
        return ""

    key = ""
    digits = ord('9') - ord('0') + 1
    letters = ord('Z') - ord('A') + 1

    for i in range(length):
        randNumber = randrange(0, digits + 2 * letters)
        if randNumber < digits:
            key += chr(randNumber + ord('0'))
        elif randNumber >= digits and randNumber < letters + digits:
            key += chr(randNumber + ord('A') - digits)
        else:
            key += chr(randNumber + ord('a') - digits - letters)
    return key


class EmployeesDataBase:
    def __init__(self):
        self.__emp_hist_dict = {}
        self.__emp_name_dict = {}
        self.__rfid_emp_dict = {}
        self.__emp_rfid_dict = {}
        self.__load_data()
        self.__lock = threading.Lock()

    def __clear_dictionaries(self):
        self.__emp_hist_dict.clear()
        self.__emp_rfid_dict.clear()
        self.__emp_name_dict.clear()
        self.__rfid_emp_dict.clear()

    def __load_data(self):
        if not os.path.exists(__DATA_FILEPATH__):
            return

        self.__clear_dictionaries()

        with open(__DATA_FILEPATH__, 'rb') as dbFile:
            dbDictionaries = pickle.load(dbFile)
            self.__emp_name_dict = dbDictionaries[0]
            self.__rfid_emp_dict = dbDictionaries[1]
            self.__emp_hist_dict = dbDictionaries[2]

        # create emp_rfid dictionary
        for item in self.__rfid_emp_dict.items():
            (rfid_uid, emp_uid) = item
            self.__emp_rfid_dict[emp_uid] = rfid_uid

    def __serialize_data(self):
        with open(__DATA_FILEPATH__, 'wb') as dbFile:
            dbDictionaries = []
            dbDictionaries.append(self.__emp_name_dict)
            dbDictionaries.append(self.__rfid_emp_dict)
            dbDictionaries.append(self.__emp_hist_dict)
            pickle.dump(dbDictionaries, dbFile)

    def save(self):
        with self.__lock:
            self.__serialize_data()

    def __remove_employee_from_dict(self, emp_uid):
        """
        Returns:\n 
        \tNone 
        """
        if emp_uid not in self.__emp_name_dict.keys():
            return

        del self.__emp_hist_dict[emp_uid]
        del self.__rfid_emp_dict[self.__emp_rfid_dict[emp_uid]]
        del self.__emp_rfid_dict[emp_uid]
        del self.__emp_name_dict[emp_uid]

    def __validate_input(self, rfid_uid):
        return isinstance(rfid_uid, int)

    def addEntry(self, rfid_uid, rfid_terminal='terminal', date=datetime.datetime.now()):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.NoSuchEmployeeError
        """
        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        with self.__lock:
            emp_uid = self.__rfid_emp_dict[rfid_uid]

            # update emp_history dictionary
            self.__emp_hist_dict[emp_uid].append(
                tuple([date.day, date.month, date.year, date.hour, date.minute, rfid_terminal]))

    def addEmployee(self, rfid_uid, emp_uid="", name=""):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.RfidAlreadyUsedError
        \tdata.EmployeeRecordAlreadyExistsError
        """
        if not self.__validate_input(rfid_uid):
            raise InvalidInputDataError

        if rfid_uid in self.__rfid_emp_dict.keys():
            raise RfidAlreadyUsedError

        with self.__lock:
            if emp_uid == "":
                emp_uid = generateKey(__DEFAULT_KEY_LEN__)
                while emp_uid in self.__emp_name_dict.keys():
                    emp_uid = generateKey(__DEFAULT_KEY_LEN__)
            elif emp_uid in self.__emp_name_dict.keys():
                raise EmployeeRecordAlreadyExistsError

            if name == "":
                name = emp_uid

            # add new employee to dictionaries
            self.__emp_name_dict[emp_uid] = name
            self.__rfid_emp_dict[rfid_uid] = emp_uid
            self.__emp_rfid_dict[emp_uid] = rfid_uid
            self.__emp_hist_dict[emp_uid] = []

    def deleteEmployee(self, rfid_uid, delHistory=True):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.NoSuchEmployeeError
        \tdata.DataBaseError
        """
        if not self.__validate_input(rfid_uid):
            raise InvalidInputDataError

        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        with self.__lock:
            emp_uid = self.__rfid_emp_dict[rfid_uid]
            self.__remove_employee_from_dict(emp_uid)

    def modifyEmpName(self, rfid_uid, newName):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.NoSuchEmployeeError
        """
        if not self.__validate_input(rfid_uid):
            raise InvalidInputDataError

        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        with self.__lock:
            emp_uid = self.__rfid_emp_dict[rfid_uid]
            self.__emp_name_dict[emp_uid] = newName

    def modifyEmpRFID(self, rfid_uid, new_rfid_uid):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.NoSuchEmployeeError
        \tdata.RfidAlreadyUsedError
        """
        if not self.__validate_input(rfid_uid) or not self.__validate_input(new_rfid_uid):
            raise InvalidInputDataError

        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        if new_rfid_uid in self.__rfid_emp_dict.keys():
            raise RfidAlreadyUsedError

        with self.__lock:
            emp_uid = self.__rfid_emp_dict[rfid_uid]
            del self.__rfid_emp_dict[rfid_uid]
            self.__rfid_emp_dict[new_rfid_uid] = emp_uid
            self.__emp_rfid_dict[emp_uid] = new_rfid_uid

    def getEmployeesDataSummary(self, includeHistory=True):
        """
        if (includeHistory == False) then list 'history' in every tuple is empty\n
        Returns:\n
        \tlist dataSummary:
        \t(list of tuple(str emp-uid, str emp-name, int rfid-uid, list history) for each employee)
        Throws exceptions:\n
        \tNone
        """
        dataSummary = []
        for emp_uid in self.__emp_name_dict.keys():
            name = str(self.__emp_name_dict[emp_uid])
            rfid_uid = self.__emp_rfid_dict[emp_uid]
            if includeHistory:
                history = self.__emp_hist_dict[emp_uid][:]
            else:
                history = []
            dataSummary.append((str(emp_uid), name, rfid_uid, history))
        return dataSummary

    def getEmpName(self, rfid_uid):
        """
        Returns:\n
        \tstr employee-name
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.NoSuchEmployeeError
        """
        if not self.__validate_input(rfid_uid=rfid_uid):
            raise InvalidInputDataError

        if rfid_uid in self.__rfid_emp_dict.keys():
            return str(self.__emp_name_dict[self.__rfid_emp_dict[rfid_uid]])
        else:
            raise NoSuchEmployeeError

    def generateReport(self, rfid_uid):
        """
        Returns:\n
        \tstr path-to-report
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.NoSuchEmployeeError
        \tdata.NoDataError
        """
        if not self.__validate_input(rfid_uid=rfid_uid):
            raise InvalidInputDataError

        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        emp_uid = self.__rfid_emp_dict[rfid_uid]

        # at least two entries needed
        if len(self.__emp_hist_dict[emp_uid]) < 2:
            raise NoDataError

        if not os.path.exists(__REPORT_DIR_PATH__):
            os.mkdir(__REPORT_DIR_PATH__)

        with self.__lock:
            workDays = []  # date of entrance, date of leave, delta_time
            isEntrance = True
            (day, month, year, hour, minute,
             terminal) = self.__emp_hist_dict[emp_uid][0]
            prevDate = datetime.datetime(year, month, day, hour, minute)

            for entry in self.__emp_hist_dict[emp_uid][1:]:
                isEntrance = not isEntrance
                (day, month, year, hour, minute, terminal) = entry
                if isEntrance:
                    prevDate = datetime.datetime(
                        year, month, day, hour, minute)
                else:
                    currentDate = datetime.datetime(
                        year, month, day, hour, minute)
                    workDays.append(
                        (prevDate, currentDate, (currentDate - prevDate)))

            filePath = f"{__REPORT_DIR_PATH__}" \
                f"{self.__emp_name_dict[emp_uid].replace(' ', '_')}_" \
                f"{datetime.datetime.now().strftime('%b-%d-%Y-%H-%M-%S')}" \
                f"{__REPORT_EXTENSION__}"

            with open(filePath, "w") as file:
                for workDay in workDays:
                    file.write(
                        f"{workDay[0].strftime('%d/%m/%Y %H:%M:%S')};{workDay[1].strftime('%d/%m/%Y %H:%M:%S')};{int(workDay[2].total_seconds())}\n")
        return filePath


#### exceptions ####

class DataBaseError(Exception):
    pass


class EmployeeRecordAlreadyExistsError(DataBaseError):
    pass


class NoSuchEmployeeError(DataBaseError):
    pass


class NoDataError(DataBaseError):
    pass


class RfidAlreadyUsedError(DataBaseError):
    pass


class InvalidInputDataError(DataBaseError):
    pass

