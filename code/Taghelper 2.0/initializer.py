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



    dbcursor.execute(query)

    
    connection.commit()






# Create an instance of tkinter frame
tkwindow = Tk()
# Set the geometry of tkinter frame
tkwindow.geometry("700x350")



# Used to define required columns for each specific database table. Also defines field data type that will be used for validation.



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
      
      Label(tkwindow, text=str(filepath), font=('Aerial 11'))
 

def getColHeaders(path: str, sheet: str) -> list:
    """
    Return a list of all column headers in a worksheet.

    Parameters:
        str path: The (explicit) path to the Excel workbook being read.
        str sheet: The name of the worksheet tab within the used workbook.

    Return:
        list headers: A list of all values in the first row of a worksheet.
    """

    workbook = openpyxl.load_workbook(path, data_only=True)
    worksheet = workbook[sheet]

    numCols = worksheet.max_column
    headers = []
    for i in range(1, numCols+1):
        headers.append(str(worksheet.cell(row=1, column=i).value))

    return headers

def mapNeededCols(colKey: dict, headers: list) -> dict:
    """ 
    Creates a mapping of required col names (given by a column key list) to their SPREADSHEET indices.
    Spreadsheet indices start at 1, not 0.

    Parameters:
        dict colKey: A configuration dictionary that describes the required features of a specific database table. Contains requried column names and their respective data types. Pairing is str:class.
        list headers: A list containing all headers in a worksheet.

    Return:
        dict colMap: A dictionary that maps the required column names to their spreadsheet index in the input sheet. Pairing is str:int.
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
        return

    print(colMap)
    return colMap


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
        
def initialize(data: dict, colKey: dict, databaseTable: str):
    """
        A wrapper function that loops through all rows in a data dictionary and calls insertMultipleValues to insert it to the database.

        Parameters:
            dict data: A dictionary that maps the rowNum/UID to a list of data values in that row. Pairing is str:list.
            dict colKey: A configuration dictionary that describes the required features of a specific database table. Contains requried column names and their respective data types. Pairing is str:class.
            str databaseTable: The name of the database table being inserted to.

        Return:
            void
    """
    assert len(data[next(iter(data))]) == len(colKey.keys()), "Column Key used for initialize function must be the same as the one corresponding to the data."
    for row in data:
        insertMultipleValues(databaseTable, colKey.keys(), data[row])

    return

def validateTypes(data: dict, colKey: dict):
    """
        A function that ensures all values in a data dictionary are the correct type for their respective database column.

        Parameters:
            dict data: A dictionary that maps the rowNum/UID to a list of data values in that row. Pairing is str:list.
            dict colKey: A configuration dictionary that describes the required features of a specific database table. Contains requried column names and their respective data types. Pairing is str:class.

        Return:
            bool failed: True if at least one value is the wrong type. False if all values are the proper type.
    """
    failed = False


    for row in data:
        for i in range(0, len(data[row])):
            if type(data[row][i]) != list(colKey.values())[i]:
                logging.warning(f"Warning: Value {data[row][i]} in Row/UID {row}, Column {list(colKey.keys())[i]} is of improper type. Expected: {list(colKey.values())[i]}. Got {type(data[row][i])}. Please correct this before uploading!")
                failed = True

    return failed

# def printtest():
#     print(getColHeaders(file_path))


def uploadSheet(path: str, colKey: dict, firstDataRow: int, lastDataRow: int, databaseTable: str, sheetName: str): # TODO Add Guard Clause for mapNeededCols
    
    columnHeaders = getColHeaders(path, sheetName)
    colMap = mapNeededCols(colKey, columnHeaders)
    data, failed = accumDataByRow(colMap, firstDataRow, lastDataRow, path)
    print(data)
    if failed:
        logging.error("ABORTING FOR EMPTY CELLS")
        return 1
    failed = validateTypes(data, colKey)
    if failed:
        logging.error("ABORTING FOR IMPROPER TYPING")
        return 1
    initialize(data, colKey, databaseTable)
    return 0

PATH = 'C:\\Users\\topplab\\Desktop\\Book1.xlsx'
_ = uploadSheet(PATH, REQUIRED_COLS["central"], 2, 44, "init2", "TestSheet1")


# PATH = 'C:\\Users\\topplab\\Desktop\\Book1.xlsx'
# ch = getColHeaders(PATH,"TestSheet1")
# cm = mapNeededCols(REQUIRED_COLS["central"],ch)
# d, _ = accumDataByRow(cm, 2, 44, PATH)
# _ = validateTypes(d, REQUIRED_COLS["central"])
# initialize(d, REQUIRED_COLS["central"], "init2")


# insertValue("test", "uid", "IT WORKS")

# ttk.Button(tkwindow, text="Broworksheete", command=open_file).pack(pady=20)
# ttk.Button(tkwindow, text="test", command=printtest).pack(pady=20)

# tkwindow.mainloop()

dbcursor.close()
connection.close()
