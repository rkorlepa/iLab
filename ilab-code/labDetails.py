#!/ws/rkorlepa-sjc/python/bin/python

import xlrd

from libilab import *
from libilab.Database import *

book = xlrd.open_workbook("sjc06-104-lab.xlsx")
print "The number of worksheets is", book.nsheets
print "Worksheet name(s):", book.sheet_names()
sh = book.sheet_by_index(0)
print sh.name, sh.nrows, sh.ncols
row_dicts = ({'model':sh.cell_value(rowx=i, colx=4), 
             'serial_num': sh.cell_value(rowx=i, colx=6),
             'lab': sh.cell_value(rowx=i, colx=7),
             'aisle': sh.cell_value(rowx=i, colx=8),
             'location': sh.cell_value(rowx=i, colx=9),
             'user': sh.cell_value(rowx=i, colx=1)} for i in range(1,sh.nrows))

sjc06_104.insert_many(row_dicts).execute()
