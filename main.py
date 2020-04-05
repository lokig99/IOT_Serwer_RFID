#!/usr/bin/env python3

import os, time, keyboard
import RPi.GPIO as GPIO

def main():
    while True:  
        if keyboard.is_pressed('a'):  
            print('You Pressed A Key!')
            time.sleep(0.2)
            

if __name__ == "__main__":
    main()