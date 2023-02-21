import mariadb
import sys
import openpyxl
from openpyxl import Workbook


wb = load_workbook(filename='testwrite.xlsx')
ws = wb["Sheet1"]
treeData = [["Type", "Leaf Color", "Height"], ["Maple", "Red", 549], ["Oak", "Green", 783], ["Pine", "Green", 1204]]

for row in treeData:
    ws.append(row)

wb.save("..\\createdfile.xlsx")