import mariadb
import sys
import openpyxl
from openpyxl import Workbook

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
import os

import getpass

LASTID = None
FIRSTNEWID = None
FILE_PATH = None

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

cur = conn.cursor()



# Create an instance of tkinter frame
win = Tk()

# Set the geometry of tkinter frame
win.geometry("700x350")
win.title("TagHelper")
win.configure(bg='#b3d98d')

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
    assert conn != None, "No database connection"

    query = f"INSERT INTO {dbTable} ({dbCol}) VALUES (?)"

    val = (value,)

    cur.execute(query,val)

    
    conn.commit()

def open_file():
    '''
    Opens a choose file widget
    '''
    global FILE_PATH
    file = filedialog.askopenfile(mode='r', filetypes=[('Excel', '*.xlsx')])
    if file:
      filepath = os.path.relpath(file.name)
      print(filepath)
      FILE_PATH = filepath
 
      assert FILE_PATH != None, "Should have a file path"
      assert os.path.isfile(FILE_PATH)
      
      Label(win, text=str(filepath), font=('Aerial 11')).pack()

def insertAllCellsInCol(path, colNum, firstDataRow=1):
    global FIRSTNEWID
    global LASTID
    '''
    Reads an entire column from open xlsx sheet and inserts all values in sequential order to connected database.

    Parameters:
        str path (The path to the .xlsx finle to upload)
        int colNum (The column of the database intended to be uploaded. Column numbers increment from 1 starting on left of xlsx document. (A is 1, B is 2, etc.))
        int firstDataRow (The first row in the spreadsheet containing data needing to be pulled. Default value 1. Overridden in examples where a spreadsheet contains headings on the first few rows etc.)


    Return:
        void
    '''
    
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active

    row = ws.max_row #rows in sheet
    column = ws.max_column #cols in sheet


    confirm = input("Are you sure you want to insert " + str(row) + " values to the database?\nType YES to continue.\n")
    if confirm != "YES":
        print("Exiting...")


    for i in range(firstDataRow, row + 1):
        
        cell = ws.cell(row = i, column = colNum)
        insertValue("tags","UUid",cell.value)

    lastId = cur.lastrowid
    firstNewId = lastId - row + firstDataRow

    # print(lastId)
    # print(firstNewId)

    FIRSTNEWID =firstNewId
    LASTID = lastId


    # wb.save(path)

    conn.commit()
    wb.close()




def write_wb(path, firstid, lastid, col_n, startrow=1):
    '''
    Writes to a column (col_n) of (path).xlsx the values from (firstid) to (lastid) starting on row (startrow) and incrementing down the column.

    Parameters:
        str path (The path to the .xlsx file to write to. Must end in .xlsx.)
        int firstid (The first uid assigned to the first row to be written to.)
        int lastid (The last id belonging to the last row in this sheet.)
        int col_n (The column to write id values to. Sheet columns are idexed from left to right starting at 1. (A is 1, B is 2, etc.))
        int startrow [optional] (The first row that contains data needing an id value (not col headers etc.). Default value 1 (row 1).)

    Return:
        void

    '''
    wb = openpyxl.load_workbook(path, data_only=True)
    
   
    ws = wb.active
    rowi = startrow

    assert firstid != None, "Must insert values to generate ids"
    assert lastid != None, "Must insert values to generate ids"

    for i in range(firstid, lastid+1):
        cell = ws.cell(row = rowi, column = col_n)
        cell.value = str(i)
        rowi+=1

    wb.save(path)
    wb.close()
    print("write successful")


#tkinter window stuff
file_label = Label(win, text="Select a file to upload", font=('Georgia 13')).pack(pady=10)



ttk.Button(win, text="Browse", command=open_file).pack(pady=20)

colnum_label = Label(win, text="Enter the col number containing barcode strings:", font=('Georgia 13')).pack(pady=10)

col_num_E = Entry(win,font=('Georgia 13'),width=40)
col_num_E.pack(pady=20)

rownum_label_bc = Label(win, text="Enter the first row number containing barcode strings:", font=('Georgia 13')).pack(pady=10)

row_num_E_bc = Entry(win,font=('Georgia 13'),width=40)
row_num_E_bc.pack(pady=20)

ttk.Button(win, text="upload", command=lambda: insertAllCellsInCol(FILE_PATH, int(col_num_E.get()), firstDataRow=int(row_num_E_bc.get())) ).pack(pady=20)







val_label = Label(win, text="Enter the col number that will contain Uids.", font=('Georgia 13')).pack(pady=10)

val_E = Entry(win,font=('Georgia 13'),width=40)
val_E.pack(pady=20)

rownum_label = Label(win, text="Enter the first row number requiring a Uid", font=('Georgia 13')).pack(pady=10)

row_num_E = Entry(win,font=('Georgia 13'),width=40)
row_num_E.pack(pady=20)



    

ttk.Button(win, text="write", command=lambda: write_wb(FILE_PATH, FIRSTNEWID, LASTID, int(val_E.get()), startrow=int(row_num_E.get()))).pack(pady=20)

win.mainloop()




