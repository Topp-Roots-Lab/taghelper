import mariadb
import sys
import openpyxl
import getpass

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
import os

from . import helper



try:
	conn = mariadb.connect(
		user="topplab",
		password=getpass.getpass(prompt='Database user password: '),
		host="10.16.0.101",
		port=3306,
		database="tag_server"
	)
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
	