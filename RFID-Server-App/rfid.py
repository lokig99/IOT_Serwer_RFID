import time, keyboard
from config import * # pylint: disable=unused-wildcard-import

sleepTime = 0.5

def rfidRead(): 
    if keyboard.is_pressed('ctrl + 1'):  
        #print('card uid = 110')
        time.sleep(sleepTime)
        return 110
    elif keyboard.is_pressed('ctrl + 2'):
        #print('card uid = 432')
        time.sleep(sleepTime)
        return 432
    elif keyboard.is_pressed('ctrl + 3'):
        #print('card uid = 734')
        time.sleep(sleepTime)
        return 734
    elif keyboard.is_pressed('ctrl + 4'):
        #print('card uid = 234')
        time.sleep(sleepTime)
        return 234
    elif keyboard.is_pressed('ctrl + 5'):
        #print('card uid = 634')
        time.sleep(sleepTime)
        return 634
    elif keyboard.is_pressed('ctrl + 6'):
        #print('card uid = 900')
        time.sleep(sleepTime)
        return 900
    elif keyboard.is_pressed('ctrl + 7'):
        #print('card uid = 1002')
        time.sleep(sleepTime)
        return 1002
    elif keyboard.is_pressed('ctrl + 8'):
        #print('card uid = 784')
        time.sleep(sleepTime)
        return 784
    else:
        return -1
