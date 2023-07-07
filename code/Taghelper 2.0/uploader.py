# <Dylan Fritz - dfritz1211@gmail.com>
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


REQUIRED_COLS = {
    "central": {"Location": int,
                "Date": str,
                "Project": int}
}

try:
    connection = mariadb.connect(
        user=os.getlogin(),
        password=getpass.getpass(prompt='Database user password: '),
        host="10.16.0.101", #Nebula's relational ip!
        port=3306,
        database="testing"
    )
    dbcursor = connection.cursor()
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)


def getColHeaders(path: str, sheet: str) -> list:
    """
    Return a list of all column headers in a worksheet.
    """

    workbook = openpyxl.load_workbook(path, data_only=True)
    worksheet = workbook[sheet]

    numCols = worksheet.max_column
    headers = []
    for i in range(1, numCols+1):
        headers.append(str(worksheet.cell(row=1, column=i).value))

    return headers

def mapNeededCols(colKey: dict, headers: list):
    """ 
    Creates a mapping of required col names (given by a column key list) to their SPREADSHEET indices.
    Spreadsheet indices start at 1, not 0.

    Parameters:
        dict colKey: A configuration dictionary that describes the required features of a specific database table. Contains requried column names and their respective data types. Pairing is str:class.
        list headers: A list containing all headers in a worksheet.

    Return:
        dict colMap: A dictionary that maps the required column names to their spreadsheet index in the input sheet. Pairing is str:int.
        bool failed: A status boolean that is True if the input sheet is missing a required column and False if all required columns are present.
    """
    colMap = {}
    failed = False
    failedList = []
    for key in colKey.keys():
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


    print(colMap)
    return colMap, failed



def accumDataByUid(colMap: dict, firstRow: int, lastRow: int, path: str):
    """
    Takes a colMap and maps data in required columns to UID.

    Parameters:
        dict colMap: A dictionary that maps the required column names to their spreadsheet index in the input sheet.
        int firstRow: A number that signifies the first row in the input spreadsheet that contains data needing to be uploaded.
        int lastRow: A number that signifies the last row in the input spreadsheet that contains data needing to be uploaded.
        str path: The (explicit) path to the Excel workbook being read.

    Return:
        dict data: A dictionary that maps the UID to a list of data values in that row. Pairing is str:list.
        bool failed: True if some cells were empty. False if all cells contained a value.
    """
    data = {}
    badCells = []
    failed = False
    workbook = openpyxl.load_workbook(path, data_only=True)
    worksheet = workbook["TestSheet1"]
    for row in range(firstRow, lastRow+1):
        data[str(worksheet.cell(row=row, column=colMap["UID"]).value)] = []
    for header in colMap:
        for row in range(firstRow, lastRow+1):
            cell = worksheet.cell(row=row, column=colMap[header])
            if cell.value != None:
                data[str(worksheet.cell(row=row, column=colMap["UID"]).value)] += [cell.value]
            else:
                failed = True
                badCells += [(row, header, colMap[header])]
    

    
    if failed:
        logging.warning("The Following cells are empty! Please check sheet and continue after updating!")
        for t in badCells:
            print(f"Row: {t[0]}, Col: {t[2]}, Col Heading: {t[1]}")


    return data, failed

def accumDataByRow(colMap: dict, firstRow: int, lastRow: int, path: str):
    """
    Takes a colMap and maps data in required columns to row number.

    Parameters:
        dict colMap: A dictionary that maps the required column names to their spreadsheet index in the input sheet.
        int firstRow: A number that signifies the first row in the input spreadsheet that contains data needing to be uploaded.
        int lastRow: A number that signifies the last row in the input spreadsheet that contains data needing to be uploaded.
        str path: The (explicit) path to the Excel workbook being read.

    Return:
        dict data: A dictionary that maps the row number to a list of data values in that row. Pairing is str:list.
        bool failed: True if some cells were empty. False if all cells contained a value.
    """
    data = {}
    badCells = []
    failed = False
    workbook = openpyxl.load_workbook(path, data_only=True)
    worksheet = workbook["TestSheet1"]
    for row in range(firstRow, lastRow+1):
        data[str(row)] = []
    for header in colMap:
        for row in range(firstRow, lastRow+1):
            cell = worksheet.cell(row=row, column=colMap[header])
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


