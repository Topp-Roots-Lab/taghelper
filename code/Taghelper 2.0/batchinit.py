# <Dylan Fritz - dfritz1211@gmail.com>
import mariadb
import sys
import openpyxl
from openpyxl import Workbook

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
import os
import shutil

import getpass

from dbhelper import *

import logging

import argparse

class MissingInfoException(Exception):
    def __init__(self, type) -> None:
        self.type = type
        self.message = f"ABORTING FOR MISSING INFO: {type}"
        super().__init__(self.message)

class ImproperTypingException(Exception):
    def __init__(self) -> None:
        self.message = f"ABORTING FOR IMPROPER TYPING"
        super().__init__(self.message)



def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Input folder path")
    parser.add_argument("first_row", type=int, help="The first row number containing data. MUST BE THE SAME FOR ALL FILES IN INPUT")

    parser.add_argument("-d", "--dev", action="store_true", help="Print all debug text.")
    parser.add_argument("-s", "--silent", action="store_true", help="Don't print anything except output and error to console.")

    args = parser.parse_args()

    return args





    


    











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




def initSheet(path: str, colKey: dict, firstDataRow: int, lastDataRow: int, databaseTable: str, sheetName: str, runIfFailed=False) -> int: 

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
    data, failed = accumDataByRow(colMap, firstDataRow, lastDataRow, path, sheetName)
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

#PATH = 'C:\\Users\\topplab\\Desktop\\TEST\\IN\\Book1.xlsx'
#_ = initSheet(PATH, REQUIRED_COLS["central"], 2, 44, "central", "Initialize")


def batchInit(folderPath: str, firstDataRow: int):
    """
    A function that runs the initialization function on multiple files in a single provided input directory. The function then creates directories for files that were uploaded successfully and those which were not uploaded due to an error. 

    Parameters:
        str folderPath: The file path to the input directory.
        int firstDataRow: The first row containing data. MUST BE THE SAME FOR ALL FILES INPUTTED.
    Return:
        void
    """
    assert not folderPath.endswith("\\"), "Input dir cannot end with a slash"
    ckey = REQUIRED_COLS["central"]
    files = [x for x in os.listdir(folderPath) if x.endswith(".xlsx")] #all files in the input directory that are .xlsx
    parentDir = os.path.dirname(folderPath)


    successDirPath = os.path.join(parentDir, "SUCCESS")
    if not os.path.exists(successDirPath):
        os.mkdir(successDirPath)

    failedDirPath = os.path.join(parentDir, "FAILED")
    if not os.path.exists(failedDirPath):
        os.mkdir(failedDirPath)

    print(files)

    for file in files:
        print(f"Now Reading {file}.")
        abspath = os.path.join(folderPath, file)
        print(abspath)

        workbook = openpyxl.load_workbook(abspath, data_only=True)
        worksheet = workbook["Initialize"]
        lRow = worksheet.max_row
        workbook.close()

        print(f"LAST ROW: {lRow}")

        failed = initSheet(abspath, ckey, firstDataRow, lRow, "central", "Initialize")

        if failed:
            shutil.move(abspath, os.path.join(failedDirPath, file))
        else:
            shutil.move(abspath, os.path.join(successDirPath, file))



if __name__ == "__main__":
    args = options()

    print(args.dev)
    print(args.silent)
    if args.dev:
        logging.basicConfig(level=logging.DEBUG)
    elif args.silent:
        logging.basicConfig(level=logging.WARNING)
    else:
        print("we made it")
        logging.basicConfig(level=logging.INFO)

    logging.debug("debug")
    logging.info("info")

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


    
    batchInit(args.path, args.first_row)


    dbcursor.close()
    connection.close()

