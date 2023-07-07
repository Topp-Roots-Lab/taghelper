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




def uploadSheet(path: str, colKey: dict, firstDataRow: int, lastDataRow: int, databaseTable: str, sheetName: str) -> int: 
    
    columnHeaders = getColHeaders(path, sheetName)
    colMap, failed = mapNeededCols(colKey, columnHeaders)
    if failed:
        logging.error("ABORTING FOR MISSING REQURIED COLUMNS")
        return 1
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
