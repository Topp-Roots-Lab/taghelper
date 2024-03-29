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

import argparse

import shutil



def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to the sheet.")
    parser.add_argument("first-row", type=int, help="The first row number containing data.")
    parser.add_argument("last-row", type=int, help="The last row number containing data.")
    parser.add_argument("sheet-name", type=str, help="The name of the worksheet to upload.")

    parser.add_argument("-d", "--dev", action="store_true", help="Print all debug text.")
    parser.add_argument("-s", "--silent", action="store_true", help="Don't print anything except output and error to console.")

    args = parser.parse_args()

    return args

logging.basicConfig(level=logging.DEBUG)






REQUIRED_COLS = {
    "central": {"Location": int,
                "Year": str, 
                "Project": int},
    "biomass": {
                "UID": int,
                "Mass": float,
                "Genotype": str,
                "Range": int,
                "Col": int,
                "Plot": int, #TODO Find some way to allow this to be null or not exist
                "Field": str,
                "SampleNum": int,
                "SampleType": str,
                "Date": str,
                "Barcode": str},
    "crown":   {
                "UID": int,
                "Genotype": str,
                "Range": int,
                "Col": int,
                "Plot": int, #TODO Find some way to allow this to be null or not exist
                "Field": str,
                "SampleNum": int,
                "SampleType": str,
                "Date": str,
                "Barcode": str},
    

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





def insertValue(dbTable,dbCol,value):
    '''
    Inserts a single value to the connected database

    Parameters:
        str dbTable (name of table in connected database)
        str dbCol (name of col in connected database)
        str value (what is to be inserted)


    Return:
        void

    '''
    global dbcursor, connection
    assert connection != None, "No database connection"

    query = f"INSERT INTO {dbTable} ({dbCol}) VALUES ('{value}')"

    # val = (value,)

    

    # dbcursor.execute(query,val)
    dbcursor.execute(query)

    
    connection.commit()


def insertMultipleValues(table: str, cols: list, vals: list): 
    """
        Inserts a list of values into the same database row.

        Parameters:
            str table: The name of the database table being inserted to.
            list cols: The list of column names corresponding to the values being added. Assumes the columns and values are in the same order.
            list vals: The actual list of values being pushed to database.
        
        Return: 
            int id: The UID of the row uploaded.
    """
    global dbcursor, connection
    assert connection != None, "No database connection"

    cols = list(cols)

    logging.debug(table)

    query = f"INSERT INTO {table} ("
    for i in range(0,len(cols)):
        if i == len(cols)-1:
            query += str(cols[i])
        else:
            query += f"{str(cols[i])},"
    
    query += ") VALUES ("

    for j in range(0, len(vals)):
        logging.debug(str(vals[j]))
        if j == len(vals)-1:
            query = query + "'" + str(vals[j]) + "'"
        else:
            query = query + "'" + str(vals[j]) + "',"

    query += ")"



    dbcursor.execute(query)
    id = dbcursor.lastrowid
    
    connection.commit()
    return id



# Used to define required columns for each specific database table. Also defines field data type that will be used for validation.



        
def initialize(data: dict, colKey: dict, databaseTable: str):
    """
        A wrapper function that loops through all rows in a data dictionary and calls insertMultipleValues to insert it to the database.

        Parameters:
            dict data: A dictionary that maps the rowNum/UID to a list of data values in that row. Pairing is str:list.
            dict colKey: A configuration dictionary that describes the required features of a specific database table. Contains requried column names and their respective data types. Pairing is str:class.
            str databaseTable: The name of the database table being inserted to.

        Return:
            int firstid: The UID of the first row uploaded.
            int lastid: the UID of the last row uploaded.
    """
    firstid = None
    
    assert len(data[next(iter(data))]) == len(colKey.keys()), "Column Key used for initialize function must be the same as the one corresponding to the data."
    for row in data:
        thisid = insertMultipleValues(databaseTable, colKey.keys(), data[row])
        if firstid == None:
            firstid = thisid
    lastid = thisid
    return firstid, lastid




def initSheet(path: str, colKey: dict, firstDataRow: int, lastDataRow: int, databaseTable: str, sheetName: str) -> int: 

    """
    A function that accumulates all data in a initializer sheet, initializes the values in the database, and adds the new UIDs to the sheet.

    Parameters:
        str path: The (explicit) path to the Excel workbook being read.
        dict colKey: A configuration dictionary that describes the required features of a specific database table. Contains requried column names and their respective data types. Pairing is str:class.
        int firstDataRow: A number that signifies the first row in the input spreadsheet that contains data needing to be uploaded.
        int lastDataRow: A number that signifies the last row in the input spreadsheet that contains data needing to be uploaded.
        str databaseTable: The name of the database table being inserted to.
        str sheetName: The name of the worksheet tab within the used workbook.
    
    Return:
        int status: A status int showing if the function ran without error or exiting early. 0 if successful, 1 for early exit.
    """
    
    columnHeaders = getColHeaders(path, sheetName)
    colMap, failed = mapNeededCols(colKey, columnHeaders)
    if failed:
        logging.error("ABORTING FOR MISSING REQURIED COLUMNS")
        return 1
    data, failed = accumDataByRow(colMap, firstDataRow, lastDataRow, path, nullUid=True)
    print(data)
    if failed:
        logging.error("ABORTING FOR EMPTY CELLS")
        return 1
    failed = validateTypes(data, colKey)
    if failed:
        logging.error("ABORTING FOR IMPROPER TYPING")
        return 1
    uidCol, failed = findUidCol(columnHeaders)
    if failed:
        logging.error("ABORTING FOR MISSING UID COLUMN")
        return 1
    firstid, lastid = initialize(data, colKey, databaseTable)
    write_wb(path, firstid, lastid, uidCol, sheetName, startrow=firstDataRow)
    return 0                   

PATH = 'C:\\Users\\topplab\\Desktop\\Book1.xlsx'
#initSheet(args.path, REQUIRED_COLS["central"], args.first_row, args.last_row, "central", args.sheet_name)

# def batchInit(parentDir: str, firstRow: int, sheetName: str):
    
#     files = getFilesOfExt(parentDir, ".xlsx")
#     print(files)
#     confirm = input(f"You will be initializing these {len(files)} files. Please check the file names and press y to continue, n to quit.").upper()
#     if confirm != "Y":
#         return 
#     parent = os.path.dirname(parentDir)
#     assert not os.path.exists(f"{parent}\\Uploaded"), f"{parent}\\Uploaded\\ Should not already exist."
#     os.mkdir(f"{parent}\\Uploaded")
#     for file in files:
#         wb = openpyxl.load_workbook(file, data_only=True)
#         ws = wb[sheetName]
#         lastDataRow = ws.max_row

#         status = initSheet(file, REQUIRED_COLS["central"], firstRow, lastDataRow, "central", sheetName)
        
#     return

# batchInit('C:\\Users\\topplab\\Desktop\\TEST\\IN', 2, "TestSheet1")
# getFilesOfExt('C:\\Users\\topplab\\Desktop', ".txt")


dbcursor.close()
connection.close()
