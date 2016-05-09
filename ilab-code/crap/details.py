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

from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from Switch import Switch

import data_from_db as dbase
import definitions as defn
import ilabmail as email 


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
    switchDetails['switch_name'] = switch.switch_name
    switchDetails['switch_type'] = ""
    switchDetails['module'] = []
    switchDetails['module_type'] = []
    for modules in xml_soup.findAll('row_modinfo'):
        if 'Supervisor' in str(modules.modtype.text):
            switchDetails['switch_type'] = str(modules.model.text.lower())
        else:
            switchDetails['module'].append(str(modules.model.text))
            switchDetails['module_type'].append(str(modules.modtype.text))

    if len(switchDetails['module']) != 0:
        db.switchdetail.remove({'switch_name':switch.switch_name})
    
    detail = {}
    print "Detail added for %s" % switch.switch_name
    for i in range(0,len(switchDetails['module'])):
        detail['switch_name'] = switch.switch_name
        detail['switch_type'] = switchDetails['switch_type']
        detail['module'] = switchDetails['module'][i]
        detail['module_type'] = switchDetails['module_type'][i]
        det_id = db.switchdetail.insert_one(detail).inserted_id
        detail = {}

if __name__ == "__main__":

    db = Database('127.0.0.1', 'root', '', 'ilab')

    print "Sit back and relax will take some time..."
    print "(DO NOT CTRL+C)"

    strfile = '%ssw_details.log' % defn.log_dir
    cli_cmd = 'rm %s' % (strfile)
    subprocess.call(cli_cmd, shell=True)
    fout = file(strfile, 'a')
    logging.basicConfig(filename=strfile, format='%(asctime)s: %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    switches = db.select('switches_test',None,'*')
    for switch in switches
        sw = Switch(switch_name = str(switch['switch_name']), \
                    console_ip = str(switch['console_ip']), \
                    mgmt_ip = str(switch['mgmt_ip']), \
                    act_port = str(switch['active_port']), \
                    stnd_port = str(switch['standby_port']), \
                    switch_pwd = str(switch['switch_pwd']), \
                    console_pwd = 'nbv123', \
                    log = strfile, \
                    kick = str(switch['kickstart']), \
                    sys = str(switch['system']))
         
        switch_details(db,sw,fout)

    print "Collected all the Current Details"
