#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import tablib
from prompt_toolkit import prompt

from ilab import *
from ilab.Database import *
from ilab.Utils import * 

def create_xls_file():
    xls_data = []
    headers = ('Id', 'Switch Name', 'Telnet Issue', 'Mgmt Issue','Loader \
            Prompt', 'Pwd Issue', 'Invalid Cli', 'Sys Uptime', 'Idle Time', \
            'Supervisors','Linecards','User', 'Manager','User Type')

    for switch in Switch_Status.select():
        user = str(Switches.get(Switches.id==switch.id).user)
        manager = str(Switches.get(Switches.id==switch.id).manager)
        temp_det_sup = []
        temp_det_line = []
        for details in Switch_Details.select().where(Switch_Details.id==switch.id):
            if 'sup' in str(details.linecard).lower():
                m = re.match('\w+-([\w-]+)', str(details.linecard))
                temp_det_sup.append(m.group(1))
            else:
                m = re.match('\w+-(\w{2})', str(details.linecard))
                if m:
                    temp_det_line.append(m.group(1))
        temp_data = (str(switch.id), \
                     str(switch.switch_name), \
                     'Yes' if switch.telnet_issue == 1 else '', \
                     'Yes' if switch.mgmt_issue == 1 else '', \
                     '' if switch.loader_prompt == None else 'Yes', \
                     '' if switch.password_issue == None else 'Yes', \
                     '' if switch.invalidcli_issue == None else 'Yes', \
                     str(switch.sys_uptime) if switch.sys_uptime != None else '', \
                     str(switch.idle_time) if switch.idle_time != None else '', \
                     ','.join(temp_det_sup), \
                     ','.join(temp_det_line), \
                     user, \
                     manager,
                     str(switch.user))
        xls_data.append(temp_data)

    xls_data = tablib.Dataset(*xls_data, headers=headers)
    with open('switch_status.xls', 'wb') as f:
        f.write(xls_data.xls)

if __name__ == '__main__':
    username = prompt(u'Username: ')
    pwd = prompt(u'Password: ')
    
    if not Utils.check_user(username, pwd):
        print "Username/Password Entered is wrong"
    else:
        create_xls_file()
