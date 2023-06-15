import mariadb
import sys
import openpyxl
from openpyxl import Workbook

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
import os


FILE_PATH = None

# Create an instance of tkinter frame
win = Tk()

# Set the geometry of tkinter frame
win.geometry("700x350")

def open_file():
    global FILE_PATH
    file = filedialog.askopenfile(mode='r', filetypes=[('Excel', '*.xlsx')])
    if file:
      filepath = os.path.relpath(file.name)
      print(filepath)
      FILE_PATH = filepath
 
      assert FILE_PATH != None, "Should have a file path"
      assert os.path.isfile(FILE_PATH)
      
      Label(win, text=str(filepath), font=('Aerial 11')).pack()

# Add a Label widget
file_label = Label(win, text="Select a file to upload", font=('Georgia 13')).pack(pady=10)



# Create a Button
ttk.Button(win, text="Browse", command=open_file).pack(pady=20)

colnum_label = Label(win, text="Enter the col number", font=('Georgia 13')).pack(pady=10)


col_num_E = Entry(win,font=('Georgia 13'),width=40)
col_num_E.pack(pady=20)

rownum_label = Label(win, text="Enter the row number", font=('Georgia 13')).pack(pady=10)

row_num_E = Entry(win,font=('Georgia 13'),width=40)
row_num_E.pack(pady=20)

val_label = Label(win, text="Enter the value to write", font=('Georgia 13')).pack(pady=10)

val_E = Entry(win,font=('Georgia 13'),width=40)
val_E.pack(pady=20)

def write_wb(path, row_n, col_n, data):
    wb = openpyxl.load_workbook(path, data_only=True)
    
   
    ws = wb.active
    for i in range(1, row_n):
        cell = ws.cell(row = i, column = col_n)
        cell.value = str(data)

    wb.save(path)
    print("write successful")

# def wrapper():
#     write_wb(FILE_PATH, 1, 1, "1")


    

ttk.Button(win, text="write", command=lambda: write_wb(FILE_PATH, int(row_num_E.get()), int(col_num_E.get()), str(val_E.get())) ).pack(pady=20)

win.mainloop()


