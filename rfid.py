import time, keyboard
from config import * # pylint: disable=unused-wildcard-import

sleepTime = 0.5

def rfidRead():
    while True:  
        if keyboard.is_pressed('1'):  
            print('card uid = 110')
            time.sleep(sleepTime)
            return 110
        elif keyboard.is_pressed('2'):
            print('card uid = 432')
            time.sleep(sleepTime)
            return 432
        elif keyboard.is_pressed('3'):
            print('card uid = 734')
            time.sleep(sleepTime)
            return 734
        elif keyboard.is_pressed('4'):
            print('card uid = 234')
            time.sleep(sleepTime)
            return 234
        elif keyboard.is_pressed('5'):
            print('card uid = 634')
            time.sleep(sleepTime)
            return 634
        elif keyboard.is_pressed('6'):
            print('card uid = 900')
            time.sleep(sleepTime)
            return 900
        elif keyboard.is_pressed('7'):
            print('card uid = 1002')
            time.sleep(sleepTime)
            return 1002
        elif keyboard.is_pressed('8'):
            print('card uid = 784')
            time.sleep(sleepTime)
            return 784
