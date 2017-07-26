#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os, sys, time 
import re
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict

from libilab import *
from libilab.Database import *
from libilab.Exceptions import *
from libilab.test_database import *
from libilab.ilabmail import *
from libilab.Switch import Switch 
from libilab.n3567kSwitch import n3567kSwitch 
from libilab.n89kSwitch import n89kSwitch

from myCelery import app

n3567kList = ['n3k','n5k','n6k','n7k','xbow', 'n77']

class swUtils(object):
    @staticmethod
    def send_telnet_issue_mail(sw_type):
        telnetIssue = defaultdict(list)
        for sw_st in Switch_Status.select().where(Switch_Status.id << \
                            Switches.select(Switches.id).where(Switches.switch_type==sw_type) \
                            & Switch_Status.telnet_issue==1):
            user = Switches.get(Switches.id == sw_st.id).user
            telnetIssue[str(user)].append(str(sw_st.switch_name))
        for key,value in telnetIssue.items():
            user = str(key)
            duts = ', '.join(value)
            telnet_template = ilab_template("detailsIncorrect.txt").render(user=user, \
                    switch_names=duts)
            from_list = "mveerach@cisco.com"
            to_list = user + "@cisco.com"
            mailer = IlabEmail(from_list, to_list)
            subject = "iLab[ISSUE] Incorrect telnet/mgmt Details in iLab DB"
            mailer.set_subject(subject)
            mailer.add_line(telnet_template)
            mailer.send()
            mailer.reset()
            print "Mail sent to %s for duts %s" % (user, duts)

    @staticmethod
    def send_pwd_issue_mail(sw_type):
        pwdIssue = defaultdict(list)
        for sw_st in Switch_Status.select().where(Switch_Status.id << \
                            Switches.select(Switches.id).where(Switches.switch_type==sw_type) \
                            & Switch_Status.password_issue=='1'):
            user = Switches.get(Switches.id == sw_st.id).user
            pwdIssue[str(user)].append(str(sw_st.switch_name))
        for key,value in pwdIssue.items():
            user = str(key)
            duts = ', '.join(value)
            pwd_template = ilab_template("pwdIncorrect.txt").render(user=user, \
                    switch_names=duts)
            from_list = "mveerach@cisco.com"
            to_list = user + "@cisco.com"
            mailer = IlabEmail(from_list, to_list)
            subject = "iLab[ISSUE] Incorrect Password in iLab DB"
            mailer.set_subject(subject)
            mailer.add_line(pwd_template)
            mailer.send()
            mailer.reset()
            print "Mail sent to %s for duts %s" % (user, duts)

    @staticmethod
    def remove_first_last_lines(string):
        ind1 = string.find('\n')
        ind2 = string.rfind('\n')
        return string[ind1+1:ind2]

    @staticmethod
    @app.task
    def switch_details(switchId, fout, using):
        mysqldb = Database(DB_HOST, DB_USER, DB_PWD, DB_DATABASE)
        switch = mysqldb.select("switches", "id=%s", "*", id=switchId)[0]
        if str(switch['switch_type']).lower() in n3567kList:
                    switchObj = n3567kSwitch(switch)
        else:
                    switchObj = n89kSwitch(switch)
        switchObj.log = fout
        # Clear the data for previous entries of switch 
        del_q = mysqldb.delete("switch_details", "id=%s", switchObj.id)
        del_q = mysqldb.delete("switch_status", "id=%s", switchObj.id)
        try:
            if using[0] == 'y':
                xml = switchObj.get_switch_details_from_mgmt('ssh')
            else:
                xml = switchObj.get_switch_module_details()
            inv = swUtils.remove_first_last_lines(xml['inv'])
            uptime = swUtils.remove_first_last_lines(xml['uptime'])
            clock = swUtils.remove_first_last_lines(xml['clock']).strip()
            idletime = swUtils.remove_first_last_lines(xml['idletime']).split(':type')[0]

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

            ins_q = mysqldb.insert("switch_status", \
                                   None, \
                                   id=switchObj.id, \
                                   switch_name = switchObj.switch_name, \
                                   telnet_issue = None if using[0] == 'y' else xml['telnet_issue'], \
                                   mgmt_issue = None if using[0] == 'y' else xml['mgmt_issue'], \
                                   sys_uptime = up_dt, \
                                   idle_time = idle)

            inv = inv.replace(" ","")
            inv = inv.replace("__readonly__", "readonly")
            xml_soup = BeautifulSoup(inv, "html.parser")

            switchDetails = {}
            regexp = re.compile(r'Supervisor|supervisor|Ethernet|ethernet|Chassis|chassis')
            switchDetails['switch_name'] = switchObj.switch_name
            switchDetails['linecard'] = []
            switchDetails['module_type'] = []
            switchDetails['serial_num'] = []
            for modules in xml_soup.findAll('row_inv'):
                if regexp.search(str(modules.desc.text).lower()) is None:
                    pass
                else:
                    switchDetails['linecard'].append(str(modules.productid.text))
                    switchDetails['module_type'].append(str(modules.desc.text))
                    switchDetails['serial_num'].append(str(modules.serialnum.text))

            tempLinecard = []
            for i in range(0,len(switchDetails['linecard'])):
                ins_q = mysqldb.insert("switch_details", \
                                       None, \
                                       id = switchObj.id, \
                                       switch_name = switchObj.switch_name, \
                                       linecard = switchDetails['linecard'][i], \
                                       serial_num = switchDetails['serial_num'][i], \
                                       module_type = switchDetails['module_type'][i])
                if re.search("(?i)supervisor", switchDetails['linecard'][i]) or \
                        re.search("(?i)ethernet", switchDetails['linecard'][i]):
                    tempLinecard.append(switchDetails['linecard'][i])
            updateLCinSwitches = str(','.join(tempLinecard))
            query = mysqldb.update("switches", "id=%s", switchObj.id, linecards=updateLCinSwitches)
            print "Detail added for %s" % switchObj.switch_name
        except PasswordError:
            ins_q = mysqldb.insert("switch_status", \
                                   None, \
                                   id=switchObj.id, \
                                   switch_name = switchObj.switch_name, \
                                   password_issue=True)
        except InvalidCliError:
            ins_q = mysqldb.insert("switch_status", \
                                   None, \
                                   id=switchObj.id, \
                                   switch_name = switchObj.switch_name, \
                                   invalidcli_issue=True)
        except LoaderError:
            ins_q = mysqldb.insert("switch_status", \
                                   None, \
                                   id=switchObj.id, \
                                   switch_name = switchObj.switch_name, \
                                   loader_prompt=True)
        except TimeoutError:
            ins_q = mysqldb.insert("switch_status", \
                                   None, \
                                   id=switchObj.id, \
                                   switch_name = switchObj.switch_name, \
                                   telnet_issue=True, \
                                   mgmt_issue=True)