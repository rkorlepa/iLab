#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os
import tablib
from prompt_toolkit import prompt
from subprocess import call, check_output

from libilab import *
from libilab.Database import *
from libilab.Utils import * 
from libilab.ilabmail import *

def create_xls_file(swtype):
    xls_databook = tablib.Databook()
    xls_data_sheet1 = []
    xls_data_sheet2 = []
    headers_sheet1 = ('Id', 'Switch Name', 'Telnet Issue', 'Mgmt Issue','Loader \
            Prompt', 'Pwd Issue', 'DUT pwd', 'Invalid Cli', 'Sys Uptime', 'Idle Time', \
            'Supervisors','Linecards','User', 'Manager', 'Cost', 'User Type')
    headers_sheet2 = ('Id', 'Switch Name', 'Module Type', 'HW-PID', 'Serial \
            Number', 'User', 'Manager')

    for sw in Switches.select().where(Switches.switch_type==swtype):
        for switch in Switch_Status.select().where(Switch_Status.id==sw.id):
            dut_pwd = str(Switches.get(Switches.id==switch.id).switch_pwd)
            user = str(Switches.get(Switches.id==switch.id).user)
            user_role = str(Switches.get(Switches.id==switch.id).user_role)
            manager = str(Switches.get(Switches.id==switch.id).manager)
            temp_det_sup = []
            temp_det_line = []
            cost = 0
            for details in Switch_Details.select().where(Switch_Details.id==switch.id):
                if 'sup' in str(details.linecard).lower():
                    m = re.match('\w+-([\w-]+)', str(details.linecard))
                    add = m.group(1) + '(' + str(details.serial_num) + ')'
                    temp_det_sup.append(add)
                    temp_data_sheet2 = (str(switch.id), \
                                        str(switch.switch_name), \
                                        str(details.module_type), \
                                        str(details.linecard), \
                                        str(details.serial_num), \
                                        user,
                                        manager)
                    xls_data_sheet2.append(temp_data_sheet2)
                            
                else:
                    m = re.match('\w+-(\w{2})', str(details.linecard))
                    if m:
                        add = str(details.linecard) + '(' + str(details.serial_num) + ')'
                        temp_det_line.append(add)
                        temp_data_sheet2 = (str(switch.id), \
                                            str(switch.switch_name), \
                                            str(details.module_type), \
                                            str(details.linecard), \
                                            str(details.serial_num), \
                                            user,
                                            manager)
                        xls_data_sheet2.append(temp_data_sheet2)
                try:
                    cost = cost + Linecards.get(Linecards.linecard==str(details.linecard)).cost
                except:
                    pass
            temp_data_sheet1 = (str(switch.id), \
                                str(switch.switch_name), \
                                'Yes' if switch.telnet_issue == 1 else '', \
                                'Yes' if switch.mgmt_issue == 1 else '', \
                                '' if switch.loader_prompt == None else 'Yes', \
                                '' if switch.password_issue == None else 'Yes', \
                                '' if switch.password_issue == None else dut_pwd, \
                                '' if switch.invalidcli_issue == None else 'Yes', \
                                str(switch.sys_uptime) if switch.sys_uptime != None else '', \
                                str(switch.idle_time) if switch.idle_time != None else '', \
                                ', '.join(temp_det_sup), \
                                ', '.join(temp_det_line), \
                                user, \
                                manager,
                                cost,
                                user_role)
            xls_data_sheet1.append(temp_data_sheet1)

    xls_data_sheet1 = tablib.Dataset(*xls_data_sheet1, headers=headers_sheet1, \
            title='Complete Details')
    xls_data_sheet2 = tablib.Dataset(*xls_data_sheet2, headers=headers_sheet2, \
            title='Individual PIDs')
    xls_databook.add_sheet(xls_data_sheet1)
    xls_databook.add_sheet(xls_data_sheet2)

    with open('switch_status.xls', 'wb') as f:
        f.write(xls_databook.xls)

    u_mail = prompt(u'Mail to whom: ')
    xls_template = ilab_template("xlsmail.txt").render(user=str(u_mail))
    u_mail = str(u_mail) + '@cisco.com'
    mailer = IlabEmail('rkorlepa@cisco.com', u_mail)
    mailer.set_subject("iLab[Switch Status]")
    mailer.add_line(xls_template)
    file_path = os.getcwd() + '/switch_status.xls'
    mailer.set_attachment(file_path)
    mailer.send()
    mailer.reset()

if __name__ == '__main__':
    username = prompt(u'Username: ')
    pwd = prompt(u'Password: ')
    
    if not Utils.check_user(username, pwd):
        print "Username/Password Entered is wrong"
    else:
        swtype = prompt(u'Query for switch_type (n9k,fretta,n7k,xbow,n6k,n5k): ')
        create_xls_file(swtype)
