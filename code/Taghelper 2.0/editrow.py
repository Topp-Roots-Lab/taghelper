# <Dylan Fritz - dfritz1211@gmail.com>
import mariadb
import sys

import os

import getpass

from dbhelper import *

import logging

import argparse

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




def editRow(id: int, tableName: str, vals: list, confirm=True):
    cols = []
    query = f"UPDATE {tableName} SET"
    