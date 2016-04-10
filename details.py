#!/home/ilab/python2.7.11/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2015  The iLab Development Team
#
#  version = 3.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os, sys, time
import traceback
import pexpect
import re
import logging
import subprocess
import definitions as defn
import ilabmail as email 

from Database import Database
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from Switch import Switch
from n7kSwitch import n7kSwitch
from n9kSwitch import n9kSwitch

db = Database('127.0.0.1', 'root', '', 'ilab')
TABLE = 'switch_details'

def remove_first_last_lines(string):
    ind1 = string.find('\n')
    ind2 = string.rfind('\n')
    return string[ind1+1:ind2]

def switch_details(db,switch,fout):
    out = remove_first_last_lines(switch.get_switch_module_details(fout))
    if out == "":
        return
    out = out.replace(" ","")
    out = out.replace("__readonly__", "readonly")
    xml_soup = BeautifulSoup(out, "html.parser")

    switchDetails = {}
    regexp = re.compile(r'fabric|supervisor|system')
    switchDetails['switch_name'] = switch.switch_name
    switchDetails['linecard'] = []
    switchDetails['module_type'] = []
    switchDetails['serial_num'] = []
    for modules in xml_soup.findAll('row_inv'):
        if regexp.search(str(modules.desc.text).lower()) is not None:
            pass
        else:
            switchDetails['linecard'].append(str(modules.productid.text))
            switchDetails['module_type'].append(str(modules.desc.text))
            switchDetails['serial_num'].append(str(modules.serialnum.text))

    if len(switchDetails['linecard']) != 0:
        db.delete(TABLE, 'switch_name=%s', switch.switch_name)

    detail = {}
    print "Detail added for %s" % switch.switch_name
    for i in range(0,len(switchDetails['linecard'])):
        detail['switch_name'] = switch.switch_name
        detail['linecard'] = switchDetails['linecard'][i]
        detail['module_type'] = switchDetails['module_type'][i]
        detail['serial_num'] = switchDetails['serial_num'][i]
        db.insert(TABLE, **detail)
        detail = {}

if __name__ == "__main__":

    print "Sit back and relax will take some time..."
    print "(DO NOT CTRL+C)"

    strfile = '%ssw_details.log' % defn.log_dir
    cli_cmd = 'rm %s' % (strfile)
    subprocess.call(cli_cmd, shell=True)
    fout = file(strfile, 'a')
    logging.basicConfig(filename=strfile, format='%(asctime)s: %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    switches = db.select('switches',None,'*')
    for switch in switches:
        sw = n7kSwitch(switch)
         
        switch_details(db,sw,fout)

    print "Collected all the Current Details"
