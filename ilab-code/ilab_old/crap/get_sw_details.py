#!/home/ilab/python2.7.11/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2015  The iLab Development Team
#
#  version = 3.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os,sys,time
import re

from prettytable import PrettyTable

import definitions as defn
import data_from_db as dbase
import ilabmail as email 
import utils as util

def printDetails(det):
    print_det = ""
    coln1 = "Switch Name"
    for key,val in det.items():
        coln2 = "%s # of cards" % (key)
        print_det = PrettyTable([coln1,coln2])
        print_det.align[coln1] = "l"
        print_det.width = 2
        for switch,number in val.items():
            print_det.add_row([switch,number])
        print print_det

if __name__ == '__main__':
    db = dbase.connect_mongodb()
    switch_details = db.switchdetail
    detail = {}
    
    for lc in defn.sw_types:
        detail[lc] = {}

        for sw in switch_details.find({'module':{"$regex":lc}}):
            if str(sw['switch_name']) in detail[lc].keys():
                detail[lc][str(sw['switch_name'])] += 1
            else:
                detail[lc][str(sw['switch_name'])] = 1
        
    printDetails(detail)
