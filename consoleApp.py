#!/usr/bin/env python3
import data, rfid, config

def displayMenu():
    print("\n--- Console RFID client Menu ---")
    print("[1] Connect new terminal to server")
    print("[2] Remove connected terminal")
    print("[3] Register new RFID card for new/current employee")
    print("[4] remove RFID card")
    print("[5] scan RFID")
    print("[6] generate report for employee")
    print("[7] Exit program")
    selectOption()


def selectOption():
    try:
        option = int(input("Enter option number: "))
    except:
        print("incorrect input")
        selectOption()

    if option == 1:
        print("Option not implemented in this version")
    elif option == 2:
        print("Option not implemented in this version")
    elif option == 3:
        registerRFID()
    elif option == 4:
        removeRFID()
    elif option == 5:
        scanRFID()
    elif option == 6:
        generateReport()
    elif option == 7:
        return
    else:
        print("No such option available")
    print()
    displayMenu()

def registerRFID(verbose=True, rfid_uid_non_verbose=0):
    if verbose:
        name = input("Enter employee name: ")
        rfid_uid = RFIDsubMenu()
    else:
        rfid_uid = rfid_uid_non_verbose
        name = str(rfid_uid)

    #check if RFID card is already used
    if rfid_uid in data.rfid_emp_dict.keys():
        print(f"ERROR: Given card is already used by employee named {data.emp_name_dict[data.rfid_emp_dict[rfid_uid]]}")
        return
    
    #check if user is already registered
    if name in data.name_emp_dict.keys():
        emp_uid = data.name_emp_dict[name]
        data.modifyEmpRFID(emp_uid, rfid_uid)
        print(f"Changed RFID card UID for {name} (employee-uid='{emp_uid}')")
    else:
        #generate new employee uid
        emp_uid = data.generateKey(4)
        while emp_uid in data.emp_name_dict.keys():
            emp_uid = data.generateKey(4)

        #add new employee
        data.addEmployee(emp_uid, name, rfid_uid)
        print(f"New employee named {name} registered with employee-uid = '{emp_uid}'")

      
def removeRFID():
    rfid_uid = RFIDsubMenu()

    if rfid_uid in data.rfid_emp_dict.keys():
        emp_uid = data.rfid_emp_dict[rfid_uid]
        data.modifyEmpRFID(emp_uid, 0)
        print(f"Removed RFID card for employee named {data.emp_name_dict[emp_uid]} (employee-uid='{emp_uid}')")
    else:
        print(f"ERROR: No such RFID card UID in database as: {rfid_uid}")

def RFIDsubMenu():
    print("Select action: ")
    print("[1] Enter RFID card UID")
    print("[2] Scan RFID card")
    print("[3] go back to main menu")
    try:
        option = int(input("Enter option number: "))
    except:
        print("incorrect input")
        registerRFID()

    if option == 1:
        try:
            rfid_uid = int(input("Enter RFID card UID: "))
            return rfid_uid
        except:
            print("incorrect input")
            registerRFID()
    elif option == 2:
        return scanRFID(registerCard=False, add_entry=False)
    else:
        return

def scanRFID(registerCard=True, add_entry=True):
    print("put your card on the reader")
    rfid_uid = rfid.rfidRead()
    if add_entry:
        if rfid_uid in data.rfid_emp_dict.keys():
            emp_uid = data.rfid_emp_dict[rfid_uid]
            data.addEntry(emp_uid)
            print(f"Added new entry for employee named {data.emp_name_dict[emp_uid]} (employee-uid='{emp_uid}')")
        else:
            registerRFID(verbose=False, rfid_uid_non_verbose=rfid_uid)
    return rfid_uid


def generateReport():
    print("Select action: ")
    print("[1] Select employee with his name")
    print("[2] Select employee with his UID")
    print("[3] go back to main menu")
    try:
        option = int(input("Enter option number: "))
    except:
         print("incorrect input")
         generateReport()
    
    if option == 1:
        try:
            name = input("Enter employees name: ")
        except:
            print("incorrect input")
            registerRFID()

        if name in data.name_emp_dict.keys():
            emp_uid = data.name_emp_dict[name]
        else:
            print(f"ERROR: No such employee named {name} in database")
            return

    elif option == 2:
        emp_uid = input("Enter employees uid: ")
        if emp_uid not in data.emp_name_dict.keys():
            print(f"ERROR: No such employee with UID={emp_uid} in database")
            return
    else:
        return

    try:
        filePath = data.generateReport(emp_uid)
        print(f"Generated new report for employee named {data.emp_name_dict[emp_uid]} (employee-uid='{emp_uid}')")
        print(f"file path: {filePath}")
    except data.NoDataError:
        print(f"User has no entries")
    
    
def test():
    data.reloadData()
    displayMenu()


if __name__ == "__main__":
    test()
