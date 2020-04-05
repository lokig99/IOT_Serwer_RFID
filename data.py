#!/usr/bin/env python3
import datetime, os
from random import randrange

dataDirPath = "data/"
empHistoryDir = "emp_history/"
entryExt = ".csv"

### dictionaries ###
emp_hist_dict = {}
name_emp_dict = {}
emp_name_dict = {}
rfid_emp_dict = {}
emp_rfid_dict = {}
####################

#### exceptions ####

class NoEmployeesFileError(Exception):
    """Raised when there is no employees file in data dir"""
    pass

class EmployeesFileEmptyError(Exception):
    """Raised when employees file has no entries in it"""
    pass

####################

with open(f"{dataDirPath}{empHistoryDir}/.format.txt") as file:
    rowOffset = len(file.readline()) + 1

def generateKey(length):
    if length <= 0:
        return None
    
    key = ""
    for i in range(length):
        randNumber = randrange(0, 62)    # = 10 digits + 2*26 basic latin letter (lowercase & uppercase)
        if randNumber < 10:
            key += chr(randNumber + 48) #digits
        elif randNumber >= 10 and randNumber < 36:
            key += chr(randNumber + 55) #uppercase letters
        else:
            key += chr(randNumber + 61) #lowercase letters
    return key


def addEntry(employee_uid, date=datetime.datetime.now()):
    filePath = f"{dataDirPath}{empHistoryDir}{employee_uid}{entryExt}"

    if os.path.exists(filePath):
        file = open(filePath, "a")
    else:
        file = open(filePath, "w")

    entryText = f"{'0' + str(date.day) if date.day < 10 else date.day };" \
        f"{'0' + str(date.month) if date.month < 10 else date.month};" \
        f"{date.year};" \
        f"{'0' + str(date.hour) if date.hour < 10 else date.hour};" \
        f"{'0' + str(date.minute) if date.minute < 10 else date.minute}\n"
    file.write(entryText)
    file.close()

def clearDictionaries():
    emp_hist_dict.clear()
    emp_rfid_dict.clear()
    name_emp_dict.clear()
    emp_name_dict.clear()
    rfid_emp_dict.clear()       

def loadData():
    clearDictionaries()
    filePath = f"{dataDirPath}employees{entryExt}"
    if not os.path.exists(filePath):
        raise NoEmployeesFileError(f"there is no '{filePath}' file")
    elif os.stat(filePath).st_size == 0:
        raise EmployeesFileEmptyError(f"'{filePath}' file is empty")
    
    #create name_emp and rfid_emp dictionary entries
    with open(filePath, "r") as file:
        line = file.readline()
        while line != "":
            (emp_uid, name, rfid_uid) = line.split(';')
            name_emp_dict[name] = emp_uid
            emp_name_dict[emp_uid] = name
            rfid_emp_dict[rfid_uid] = emp_uid
            emp_rfid_dict[emp_uid] = rfid_uid
    
    #create emp_history dictionary entries
    for emp_uid in emp_name_dict.keys():
        filePath = f"{dataDirPath}{empHistoryDir}{emp_uid}{entryExt}"
        if os.path.exists(filePath):
            with open(filePath, "r") as file:




    




def addEmployee(emp_uid, name, rfid_uid):
    pass




""" with open("data/employees/aaaa.csv", "r") as file:
    line = file.readline()
    while line != "":
        entry = tuple([int(item) for item in line.split(';')])
        print(entry)
        employees['aaaa'].append(entry)
        line = file.readline()
print(employees) """


def test():
    loadData()

    emp_hist_dict[403] = ("Andrzej Kowalski", 0, [])
    emp_hist_dict[generateKey(4)] = ("Adam Nowak", 0, [])

    print(emp_hist_dict)

    for emp_uid in emp_hist_dict.keys():
        addEntry(emp_uid)

if __name__ == "__main__":
    test()

