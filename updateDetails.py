#!/home/ilab/python2.7.11/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import re
import logging
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime

from ilab import *
from ilab.Database import *
from ilab.Switch import Switch 
from ilab.n3567kSwitch import n3567kSwitch 
from ilab.n89kSwitch import n89kSwitch

def remove_first_last_lines(string):
    ind1 = string.find('\n')
    ind2 = string.rfind('\n')
    return string[ind1+1:ind2]

def switch_details(switch, fout=None):
    xml = switch.get_switch_module_details(fout)
    inv = remove_first_last_lines(xml['output'])
    uptime = remove_first_last_lines(xml['uptime'])

    # Clear the data for previous entries of switch 
    del_q = Switch_Details.delete().where(Switch_Details.switch_name==switch.switch_name).execute()
    del_q = Switch_Status.delete().where(Switch_Status.switch_name==switch.switch_name).execute()
    
    if inv == "":
        ins_q = Switch_Status.create(id=switch.id, \
                                     switch_name = switch.switch_name, \
                                     telnet_issue=xml['telnet_issue'], \
                                     mgmt_issue=xml['mgmt_issue'])
        return
    
    uptime = uptime.replace("__readonly__", "readonly")
    xml_soup = BeautifulSoup(uptime, "html.parser")
    up_dt = datetime.strptime(xml_soup.sys_st_time.text, '%a %b  %d %H:%M:%S %Y')
    ins_q = Switch_Status.create(id=switch.id, \
                                 switch_name = switch.switch_name, \
                                 telnet_issue = xml['telnet_issue'], \
                                 mgmt_issue = xml['mgmt_issue'], \
                                 idle_time = up_dt)

    inv = inv.replace(" ","")
    inv = inv.replace("__readonly__", "readonly")
    xml_soup = BeautifulSoup(inv, "html.parser")

    switchDetails = {}
    regexp = re.compile(r'fabric|system|Chassis|chassis|power|Power')
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

    for i in range(0,len(switchDetails['linecard'])):
        ins_q = Switch_Details.create(id = switch.id, \
                                      switch_name = switch.switch_name, \
                                      linecard = switchDetails['linecard'][i], \
                                      serial_num = switchDetails['serial_num'][i], \
                                      module_type = switchDetails['module_type'][i])
    print "Detail added for %s" % switch.switch_name

if __name__ == "__main__":

    print "Sit back and relax will take some time..."
    print "(DO NOT CTRL+C)"

    n3567kList = ['n3k','n5k','n6k','n7k']
    strfile = '%ssw_details.log' % LOG_DIR 
    cli_cmd = 'rm %s' % (strfile)
    subprocess.call(cli_cmd, shell=True)
    #fout = file(strfile, 'a')
    #logging.basicConfig(filename=strfile, format='%(asctime)s: %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    for switch in Switches.select().dicts():
        if str(switch['switch_type']).lower() in n3567kList:
            sw = n3567kSwitch(switch)
        else:
            sw = n89kSwitch(switch)
        switch_details(sw, fout=None)

    print "Collected all the Current Details"
