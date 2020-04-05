import rfid
import config

def displayMenu():
    print("\n--- Console RFID client Menu ---")
    print("[1] ")
    selectOption()


def selectOption():
    try:
        option = int(input("Podaj numer opcji: "))
    except:
        print("niepoprawne dane wejsciowe")
        selectOption()
    




def test():
    displayMenu()


if __name__ == "__main__":
    test()