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


