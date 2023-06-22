import mariadb
import sys
import openpyxl
from openpyxl import Workbook

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
import os

import getpass

import logging

logging.basicConfig(level=logging.DEBUG)


# # Create an instance of tkinter frame
# win = Tk()
# # Set the geometry of tkinter frame
# win.geometry("700x350")

REQUIRED_COLS = {
    "central": ["Location", "Date", "Project"]
}

file_path = None

def open_file():
    '''
    Opens a choose file widget
    '''
    global file_path
    file = filedialog.askopenfile(mode='r', filetypes=[('Excel', '*.xlsx')])
    if file:
      filepath = os.path.relpath(file.name)
      print(filepath)

      file_path = filepath
    
      assert filepath != None, "Should have a file path"
      assert os.path.isfile(filepath)
      
      Label(win, text=str(filepath), font=('Aerial 11'))
 

def getColHeaders(path):

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["TestSheet1"]

    numCols = ws.max_column
    headers = []
    for i in range(1, numCols+1):
        headers.append(str(ws.cell(row=1, column=i).value))

    return headers

def mapNeededCols(colKey, headers):
    colMap = {}
    failed = False
    failedList = []
    for key in colKey:
        try:
            if headers.index(key) >= 0:
                colMap[key] = headers.index(key)
        except ValueError:
            failed = True
            failedList.append(key)
        
    if failed:
        logging.warning('MISSING FOLLOWING REQUIRED COLUMNS:')
        for col in failedList:
            logging.warning(col)
        return

    return colMap
        


def printtest():
    print(getColHeaders(file_path))


test1 = ["key1", "key2", "key3"]
test2 = ["key1", "random", "key3", "key"]


logging.debug(mapNeededCols(test1, test2))
# ttk.Button(win, text="Browse", command=open_file).pack(pady=20)
# ttk.Button(win, text="test", command=printtest).pack(pady=20)

# win.mainloop()
