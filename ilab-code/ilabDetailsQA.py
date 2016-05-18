#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import re
import logging
from subprocess import call, check_output
from bs4 import BeautifulSoup
from datetime import datetime

from ilab import *
from ilab.Exceptions import *
from ilab.Database import *
from ilab.Switch import Switch 
from ilab.n3567kSwitch import n3567kSwitch 
from ilab.n89kSwitch import n89kSwitch

def remove_first_last_lines(string):
    ind1 = string.find('\n')
    ind2 = string.rfind('\n')
    return string[ind1+1:ind2]

def switch_details(switchObj):
    # Clear the data for previous entries of switch 
    del_q = Switch_Details.delete().where(Switch_Details.switch_name==switchObj.switch_name).execute()
    del_q = Switch_Status.delete().where(Switch_Status.switch_name==switchObj.switch_name).execute()
    try:
        xml = switchObj.get_switch_details_from_mgmt("ssh")
        inv = remove_first_last_lines(xml['inv'])
        uptime = remove_first_last_lines(xml['uptime'])
        clock = remove_first_last_lines(xml['clock']).strip()
        idletime = remove_first_last_lines(xml['idletime']).split(':type')[0]

        #Get the system uptime from xml
        uptime = uptime.replace("__readonly__", "readonly")
        xml_soup = BeautifulSoup(uptime, "html.parser")
        try:
            up_dt = datetime.strptime(xml_soup.sys_st_time.text, '%a %b  %d %H:%M:%S %Y')
        except:
            up_dt = None
        #Get idletime using clock of switch
        try:
            clock_dt = datetime.strptime(clock, '%H:%M:%S.%f %Z %a %b %d %Y')
            temp_dt = datetime.strptime(idletime, '%a %b  %d %H:%M:%S %Y')
            idle_dt = clock_dt - temp_dt
            idle = '%s' % idle_dt
        except:
            idle = None 
        ins_q = Switch_Status.create(id=switchObj.id, \
                                     switch_name = switchObj.switch_name, \
                                     telnet_issue = False, \
                                     mgmt_issue = False, \
                                     sys_uptime = up_dt, \
                                     idle_time = idle,
                                     user = 'QA')

        inv = inv.replace(" ","")
        inv = inv.replace("__readonly__", "readonly")
        xml_soup = BeautifulSoup(inv, "html.parser")

        switchDetails = {}
        regexp = re.compile(r'fabric|system|Chassis|chassis|power|Power')
        switchDetails['switch_name'] = switchObj.switch_name
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
            ins_q = Switch_Details.create(id = switchObj.id, \
                                          switch_name = switchObj.switch_name, \
                                          linecard = switchDetails['linecard'][i], \
                                          serial_num = switchDetails['serial_num'][i], \
                                          module_type = switchDetails['module_type'][i])
        print "Detail added for %s" % switchObj.switch_name
    except PasswordError:
        ins_q = Switch_Status.create(id=switchObj.id, \
                                     switch_name = switchObj.switch_name, \
                                     password_issue=True,
                                     user = 'QA')
    except InvalidCliError:
        ins_q = Switch_Status.create(id=switchObj.id, \
                                     switch_name = switchObj.switch_name, \
                                     invalidcli_issue=True,
                                     user = 'QA')
    except LoaderError:
        ins_q = Switch_Status.create(id=switchObj.id, \
                                     switch_name = switchObj.switch_name, \
                                     loader_prompt=True,
                                     user = 'QA')
    except (TimeoutError,EofError):
        ins_q = Switch_Status.create(id=switchObj.id, \
                                     switch_name = switchObj.switch_name, \
                                     telnet_issue=True, \
                                     mgmt_issue=True,
                                     user = 'QA')

if __name__ == "__main__":

    print "Sit back and relax will take some time..."
    print "(DO NOT CTRL+C)"

    n3567kList = ['n3k','n5k','n6k','n7k']
    strfile = '%ssw_details_qa.log' % LOG_DIR 
    cli_cmd = 'rm %s' % (strfile)
    call(cli_cmd, shell=True)
    fout = None
    fout = file(strfile, 'a')
    logging.basicConfig(filename=strfile, format='%(asctime)s: %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    storeManagers = ['mbandi','hahamed']
    proceed = True
    for switch in Switches.select().where(Switches.manager!="").dicts():
        proceed = True
        users = str(switch['user']).lower().split(',')
        for user in users:
            rchain = check_output(["/usr/cisco/bin/rchain","-h","-M %s" % (user)]).split()
            if not any(i in rchain for i in storeManagers):
                proceed = False
                break
        if proceed:
            if str(switch['switch_type']).lower() in n3567kList:
                switchObj = n3567kSwitch(switch)
            else:
                switchObj = n89kSwitch(switch)
            switchObj.log = fout
            switch_details(switchObj)

    print "Collected all the Current Details"
