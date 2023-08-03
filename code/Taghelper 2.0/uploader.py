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


def insertMultipleValues(table: str, cols: list, vals: list): 
    """
        Inserts a list of values into the same database row.

        Parameters:
            str table: The name of the database table being inserted to.
            list cols: The list of column names corresponding to the values being added. Assumes the columns and values are in the same order.
            list vals: The actual list of values being pushed to database.
        
        Return: 
            void
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

    logging.debug(query)

    dbcursor.execute(query)

    
    connection.commit()

def verifyUID(uid: int, table: str) -> bool:
    """
    A function that checks if a database table contains a UID value.

    Parameters:
        int uid: The UID to be verified.
        str table: The database table to check for the UID.

    Return:
        bool contained: True if the UID is present at least once in the table, False if not.
    """
    query = f"SELECT * FROM {table} WHERE {table}.UID = {str(uid)}"
    dbcursor.execute(query)
    response = []
    for t in dbcursor:
        print(t)
        response += [t]
    print(response)
    
    contained = len(response) >= 1

    return contained

def verifyDataUidsInit(data: dict) -> bool:
    """
    A function that ensures all UIDs in a data dictionary are initialized.

    Parameters:
        dict data: The data dictionary to verify.
    
    Return:
        bool failed: True if 1 or more UIDs in data is uninitialized. False if all UIDs have been initialized.
    """
    failed = False
    falseUIDs = []
    for uid in data:
        if not verifyUID(uid, "central"):
            failed = True
            falseUIDs += [uid]
    if failed:
        logging.warning("The following UIDs are in your file but have not been initialized.")
        for u in falseUIDs:
            print(u)
    return failed

def ensureUIDsNotContained(data: dict, table: str) -> bool:
    """
    A function that checks if a UID is already contained in a table.

    Parameters: 
        dict data: The data dictionary to verify.
        str table: The database table to check for the UID.
    
    Return:
        bool failed: True if 1 or more of the UIDs is already in the table. False if all UIDs are unique.
    """
    failed = False
    falseUIDs = []
    for uid in data:
        if verifyUID(uid, table):
            failed = True
            falseUIDs += [uid]
    if failed:
        logging.warning(f"The following UIDs are in your file but already have a value in this table ({table}).")
        for u in falseUIDs:
            print(u)
    return failed
        

def upload(data: dict, colKey: dict, databaseTable: str):
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
    
    assert len(data[next(iter(data))]) == len(colKey.keys()), "Column Key used for initialize function must be the same as the one corresponding to the data."
    for row in data:
        insertMultipleValues(databaseTable, colKey.keys(), data[row])




PATH = 'C:\\Users\\topplab\\Desktop\\Book1.xlsx'



def uploadSheet(path: str, sheetname: str, colKey: dict, firstDataRow: int, lastDataRow: int, databaseTable: str, allowRedundantUIDs=False) -> int:
    headers = getColHeaders(path, sheetname)
    colMap, failed = mapNeededCols(colKey, headers)
    if failed:
        logging.error("EXITING FOR MISSING REQUIRED COLUMNS")
        return 1
    data, failed = accumDataByUid(colMap, firstDataRow, lastDataRow, path, sheetname, uidAsData=True)
    if failed:
        logging.error("EXITING FOR EMPTY CELLS")
        return 1
    failed = verifyDataUidsInit(data)
    if failed:
        logging.error("EXITING FOR UNINITIALIZED UIDS")
        return 1
    
    if not allowRedundantUIDs:
        failed = ensureUIDsNotContained(data, databaseTable)
        if failed:
            logging.error("EXITING FOR REDUNDANT UIDS")
            return 1
        
    failed = validateTypes(data, colKey)
    if failed:
        logging.error("EXITING FOR MISMATCHED TYPING")
        return 1
    upload(data, colKey, databaseTable)
    return 0



uploadSheet(PATH, "TestSheet2", REQUIRED_COLS["biomass"], 2, 38, "biomass", allowRedundantUIDs=True)
