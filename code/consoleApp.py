#!/usr/bin/env python3
import rfid, config, data

def displayMenu():
    print("\n--- Console RFID client Menu ---")
    print("[1] Connect new terminal to server")
    print("[2] Remove connected terminal")
    print("[3] Register new employee with RFID card")
    print("[4] remove RFID card from employee")
    print("[5] scan RFID")
    print("[6] generate report for employee")
    selectOption()


def selectOption():
    try:
        option = int(input("Podaj numer opcji: "))
    except:
        print("niepoprawne dane wejsciowe")
        selectOption()
    print(data.emp_hist_dict)
    




def test():
    data.reloadData()
    displayMenu()


if __name__ == "__main__":
    test()