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
                "Project": int},
    "biomass": {"UID": int,
                "Biomass": int}
    
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



    dbcursor.execute(query)

    
    connection.commit()



PATH = 'C:\\Users\\topplab\\Desktop\\Book1.xlsx'
print(getColHeaders(PATH, "TestSheet2"))

