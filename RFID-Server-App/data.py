#!/usr/bin/env python3
import datetime
import os
from random import randrange

__DATA_DIR_PATH__ = "./data/"
__EMP_HISTORY_DIR_PATH__ = f"{__DATA_DIR_PATH__}emp_history/"
__DATA_EXTENSION__ = ".data"
__REPORT_EXTENSION__ = ".csv"
__EMPLOYEES_FILE_PATH__ = f"{__DATA_DIR_PATH__}employees{__DATA_EXTENSION__}"
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
        self.__name_emp_dict = {}
        self.__emp_name_dict = {}
        self.__rfid_emp_dict = {}
        self.__emp_rfid_dict = {}
        self.__reload_data()

    def __clear_dictionaries(self):
        self.__emp_hist_dict.clear()
        self.__emp_rfid_dict.clear()
        self.__name_emp_dict.clear()
        self.__emp_name_dict.clear()
        self.__rfid_emp_dict.clear()

    def __reload_data(self):
        if not os.path.exists(__DATA_DIR_PATH__):
            os.mkdir(__DATA_DIR_PATH__)

        if not os.path.exists(__EMP_HISTORY_DIR_PATH__):
            os.mkdir(__EMP_HISTORY_DIR_PATH__)

        if not os.path.exists(__EMPLOYEES_FILE_PATH__):
            open(__EMPLOYEES_FILE_PATH__, "w")

        if os.stat(__EMPLOYEES_FILE_PATH__).st_size == 0:
            return

        self.__clear_dictionaries()

        # create name_emp and rfid_emp dictionary entries
        with open(__EMPLOYEES_FILE_PATH__, "r") as file:
            line = file.readline()
            while line != "":
                (emp_uid, name, rfid_uid) = line.split(';')
                self.__name_emp_dict[name] = emp_uid
                self.__emp_name_dict[emp_uid] = name
                self.__rfid_emp_dict[int(rfid_uid)] = emp_uid
                self.__emp_rfid_dict[emp_uid] = int(rfid_uid)
                line = file.readline()

        # add entries to emp_history dictionary
        for emp_uid in self.__emp_name_dict.keys():
            self.__emp_hist_dict[emp_uid] = []
            filePath = f"{__EMP_HISTORY_DIR_PATH__}{emp_uid}{__DATA_EXTENSION__}"
            if os.path.exists(filePath):
                with open(filePath, "r") as file:
                    line = file.readline()
                    while line != "":
                        entry = tuple([int(item) for item in line.split(';')])
                        self.__emp_hist_dict[emp_uid].append(entry)
                        line = file.readline()

    def __remove_employee_from_dict(self, emp_uid):
        """
        Deletes all entries of single employee in database dictionaries
        without modifying data files on storage device or reloading whole
        database from storage.\n
        Returns:\n 
        \tNone 
        """
        if emp_uid not in self.__emp_name_dict.keys():
            return

        del self.__emp_hist_dict[emp_uid]
        del self.__rfid_emp_dict[self.__emp_rfid_dict[emp_uid]]
        del self.__name_emp_dict[self.__emp_name_dict[emp_uid]]
        del self.__emp_rfid_dict[emp_uid]
        del self.__emp_name_dict[emp_uid]

    def __validate_input(self, emp_uid="", name="", rfid_uid=0):
        if ';' in emp_uid or ';' in name:
            return False
        if not isinstance(rfid_uid, int) or rfid_uid < 0:
            return False
        return True

    def addEntry(self, rfid_uid, rfid_terminal=1, date=datetime.datetime.now()):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.NoSuchEmployeeError
        """
        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        emp_uid = self.__rfid_emp_dict[rfid_uid]
        filePath = f"{__EMP_HISTORY_DIR_PATH__}{emp_uid}{__DATA_EXTENSION__}"
        if os.path.exists(filePath):
            file = open(filePath, "a")
        else:
            file = open(filePath, "w")

        entryText = f"{date.day};{date.month};{date.year};{date.hour};{date.minute};{rfid_terminal}\n"
        file.write(entryText)
        file.close()

        # update emp_history dictionary
        self.__emp_hist_dict[emp_uid].append(
            tuple([int(item) for item in entryText.split(';')]))

    def addEmployee(self, rfid_uid, emp_uid="", name=""):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.RfidAlreadyUsedError
        \tdata.EmployeeRecordAlreadyExistsError
        """
        if not self.__validate_input(rfid_uid=rfid_uid, emp_uid=emp_uid, name=name):
            raise InvalidInputDataError

        if rfid_uid in self.__rfid_emp_dict.keys():
            raise RfidAlreadyUsedError

        if emp_uid == "":
            emp_uid = generateKey(__DEFAULT_KEY_LEN__)
            while emp_uid in self.__emp_name_dict.keys():
                emp_uid = generateKey(__DEFAULT_KEY_LEN__)
        elif emp_uid in self.__emp_name_dict.keys():
            raise EmployeeRecordAlreadyExistsError

        if os.path.exists(__EMPLOYEES_FILE_PATH__):
            file = open(__EMPLOYEES_FILE_PATH__, "a")
        else:
            file = open(__EMPLOYEES_FILE_PATH__, "w")

        if name == "":
            name = emp_uid

        file.write(f"{emp_uid};{name};{rfid_uid}\n")
        file.close()
        self.__reload_data()

    def deleteEmployee(self, rfid_uid, delHistory=True):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.NoSuchEmployeeError
        \tdata.DataBaseError
        """
        if not self.__validate_input(rfid_uid=rfid_uid):
            raise InvalidInputDataError

        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        if not os.path.exists(__EMPLOYEES_FILE_PATH__):
            self.__reload_data()
            if not os.path.exists(__EMPLOYEES_FILE_PATH__):
                raise DataBaseError

        emp_uid = self.__rfid_emp_dict[rfid_uid]

        # rewrite file without deleted employee
        with open(__EMPLOYEES_FILE_PATH__, "r") as file:
            lines = file.readlines()
        with open(__EMPLOYEES_FILE_PATH__, "w") as file:
            for line in lines:
                if line.split(';')[0] != emp_uid:
                    file.write(line)

        # delete history file
        filePath = f"{__EMP_HISTORY_DIR_PATH__}{emp_uid}{__DATA_EXTENSION__}"
        if os.path.exists(filePath) and delHistory:
            os.remove(filePath)

        self.__remove_employee_from_dict(emp_uid)

    def modifyEmpName(self, rfid_uid, newName):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.NoSuchEmployeeError
        """
        if not self.__validate_input(rfid_uid=rfid_uid, name=newName):
            raise InvalidInputDataError

        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        emp_uid = self.__rfid_emp_dict[rfid_uid]

        self.deleteEmployee(rfid_uid, delHistory=False)
        self.addEmployee(rfid_uid, emp_uid=emp_uid, name=newName)

    def modifyEmpRFID(self, rfid_uid, new_rfid_uid):
        """
        Returns:\n
        \tNone
        Throws exceptions:\n
        \tdata.InvalidInputDataError
        \tdata.NoSuchEmployeeError
        \tdata.RfidAlreadyUsedError
        """
        if not self.__validate_input(rfid_uid=rfid_uid) or not self.__validate_input(rfid_uid=new_rfid_uid):
            raise InvalidInputDataError

        if rfid_uid not in self.__rfid_emp_dict.keys():
            raise NoSuchEmployeeError

        if new_rfid_uid in self.__rfid_emp_dict.keys():
            raise RfidAlreadyUsedError

        emp_uid = self.__rfid_emp_dict[rfid_uid]
        name = self.__emp_name_dict[emp_uid]

        self.deleteEmployee(rfid_uid, delHistory=False)
        self.addEmployee(new_rfid_uid, emp_uid=emp_uid, name=name)

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

        if len(self.__emp_hist_dict[emp_uid]) == 0:
            raise NoDataError

        if not os.path.exists(__REPORT_DIR_PATH__):
            os.mkdir(__REPORT_DIR_PATH__)

        workDays = []  # date of entrance, date of leave, delta_time
        isEntrance = True
        (day, month, year, hour, minute,
         terminal) = self.__emp_hist_dict[emp_uid][0]
        prevDate = datetime.datetime(year, month, day, hour, minute)

        for entry in self.__emp_hist_dict[emp_uid][1:]:
            isEntrance = not isEntrance
            (day, month, year, hour, minute, terminal) = entry
            if isEntrance:
                prevDate = datetime.datetime(year, month, day, hour, minute)
            else:
                currentDate = datetime.datetime(year, month, day, hour, minute)
                workDays.append(
                    (prevDate, currentDate, (currentDate - prevDate)))

        filePath = f"{__REPORT_DIR_PATH__}" \
            f"{self.__emp_name_dict[emp_uid].replace(' ', '_')}_" \
            f"{datetime.datetime.now().strftime('%b-%d-%Y-%H-%M-%S')}" \
            f"{__REPORT_EXTENSION__}"

        with open(filePath, "w") as file:
            for workDay in workDays:
                file.write(
                    f"{workDay[0].strftime('%d/%m/%Y')};{workDay[1].strftime('%d/%m/%Y')};{int(workDay[2].total_seconds())}\n")
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

####################


def test():
    data = EmployeesDataBase()
    # data.addEmployee(12345)
    # data.addEmployee(1111)
    # data.addEmployee(2222)

    data.modifyEmpRFID(1111, 9999)

    print(data.getEmployeesDataSummary())


if __name__ == "__main__":
    test()
