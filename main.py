#!/usr/bin/env python3

import os, data
import consoleApp as app

def main():
    data.reloadData()
    app.displayMenu()

if __name__ == "__main__":
    main()