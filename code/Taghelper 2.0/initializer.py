#<Dylan Fritz - dfritz1211@gmail.com>
import mariadb
import sys
import openpyxl
from openpyxl import Workbook

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
import os

import getpass

from dbhelper import *

import logging

logging.basicConfig(level=logging.DEBUG)


try:
    conn = mariadb.connect(
        user=os.getlogin(),
        password=getpass.getpass(prompt='Database user password: '),
        host="10.16.0.101", #Nebula's relational ip!
        port=3306,
        database="testing"
    )
    cur = conn.cursor()
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)





def insertValue(dbTable,dbCol,value):
    '''
    Inserts a single value to the connected database

    Parameters:
        str dbTable (name of table in connected database)
        str dbCol (name of col in connected database)
        str value (what is to be inserted)
        obj cur (database cursor)
        obj con (database connection)

    Return:
        void

    '''
    global cur, conn
    assert conn != None, "No database connection"

    query = f"INSERT INTO {dbTable} ({dbCol}) VALUES ('{value}')"

    # val = (value,)

    

    # cur.execute(query,val)
    cur.execute(query)

    
    conn.commit()


# Create an instance of tkinter frame
win = Tk()
# Set the geometry of tkinter frame
win.geometry("700x350")

REQUIRED_COLS = {
    "central": ["UID","Location", "Date", "Project"]
}

file_path = None

def open_file() -> None:
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
 

def getColHeaders(path: str, sheet: str) -> list:
    """
    Return a list of all column headers in a worksheet.
    """

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet]

    numCols = ws.max_column
    headers = []
    for i in range(1, numCols+1):
        headers.append(str(ws.cell(row=1, column=i).value))

    return headers

def mapNeededCols(colKey: list, headers: list) -> dict:
    """ 
    Creates a mapping of required col names (given by a column key list) to their SPREADSHEET indices.
    Spreadsheet indices start at 1, not 0.
    """
    colMap = {}
    failed = False
    failedList = []
    for key in colKey:
        try:
            if headers.index(key) >= 0:
                colMap[key] = headers.index(key)+1 #adding 1 to change into spreadsheet index
        except ValueError:
            failed = True
            failedList.append(key)
        
    if failed:
        logging.warning('MISSING FOLLOWING REQUIRED COLUMNS:')
        for col in failedList:
            logging.warning(col)
        return

    return colMap


def accumDataByRow(colMap: dict, firstRow: int, lastRow: int, path: str):
    """
    Takes a colMap and maps data in required columns to row number.
    """
    data = {}
    badCells = []
    failed = False
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["TestSheet1"]
    for row in range(firstRow, lastRow+1):
        data[str(row)] = []
    for header in colMap:
        for row in range(firstRow, lastRow+1):
            cell = ws.cell(row=row, column=colMap[header])
            if cell.value != None:
                data[str(row)] += [cell.value]
            else:
                failed = True
                badCells += [(row, header, colMap[header])]
    

    
    if failed:
        logging.warning("The Following cells are empty! Please check sheet and continue after updating!")
        for t in badCells:
            print(f"Row: {t[0]}, Col: {t[2]}, Col Heading: {t[1]}")


    return data, failed



def accumDataByUid(colMap: dict, firstRow: int, lastRow: int, path: str):
    """
    Takes a colMap and maps data in required columns to UID.
    """
    data = {}
    badCells = []
    failed = False
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["TestSheet1"]
    for row in range(firstRow, lastRow+1):
        data[str(ws.cell(row=row, column=colMap["UID"]).value)] = []
    for header in colMap:
        for row in range(firstRow, lastRow+1):
            cell = ws.cell(row=row, column=colMap[header])
            if cell.value != None:
                data[str(ws.cell(row=row, column=colMap["UID"]).value)] += [cell.value]
            else:
                failed = True
                badCells += [(row, header, colMap[header])]
    

    
    if failed:
        logging.warning("The Following cells are empty! Please check sheet and continue after updating!")
        for t in badCells:
            print(f"Row: {t[0]}, Col: {t[2]}, Col Heading: {t[1]}")


    return data, failed
        
def uploadData(data: dict):
    return

def printtest():
    print(getColHeaders(file_path))

# PATH = 'C:\\Users\\topplab\\Desktop\\Book1.xlsx'
# ch = getColHeaders(PATH,"TestSheet1")
# cm = mapNeededCols(REQUIRED_COLS["central"],ch)
# d, _ = accumDataByUid(cm, 2, 44, PATH)
# print(d)

insertValue("test", "uid", "IT WORKS")

# ttk.Button(win, text="Browse", command=open_file).pack(pady=20)
# ttk.Button(win, text="test", command=printtest).pack(pady=20)

# win.mainloop()

cur.close()
conn.close()
