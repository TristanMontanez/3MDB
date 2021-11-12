import xlrd
from csv import writer
import os.path

workbook = xlrd.open_workbook('PRICELIST.xls')
worksheet = workbook.sheet_by_name('Sheet1')

i = 1
items = []
while i < 620:
    id = int(worksheet.cell(i, 0).value)
    name = worksheet.cell(i, 1).value
    price = int(worksheet.cell(i, 2).value)
    items.append([id, name, price])
    print([id, name, price])
    i += 1

upload_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../table/product_db.csv"))

with open(upload_path, 'a', newline='') as file_object:
    writer_object = writer(file_object)
    for entry in items:
        writer_object.writerow(entry)
    file_object.close()
