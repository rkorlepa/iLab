#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

from ilab import *
from ilab.Database import *
from ilab.ilabmail import *
from collections import defaultdict

def send_telnet_issue_mail():
    telnetIssue = defaultdict(list)
    for sw_st in Switch_Status.select(Switch_Status.id,Switch_Status.switch_name).where(Switch_Status.telnet_issue==1):
        user = Switches.get(Switches.id == sw_st.id).user
        telnetIssue[str(user)].append(str(sw_st.switch_name))
    for key,value in telnetIssue.items():
        user = str(key)
        duts = ', '.join(value)
        telnet_template = ilab_template("detailsIncorrect.txt").render(user=user, \
                switch_names=duts)
        from_list = to_list = user + "@cisco.com"
        mailer = IlabEmail(from_list, to_list)
        subject = "iLab[ISSUE] Incorrect Password in iLab DB"
        mailer.set_subject(subject)
        mailer.add_line(telnet_template)
        mailer.send()
        mailer.reset()
        print "Mail sent to %s for duts %s" % (user, duts)

if __name__ == '__main__':
    username = prompt(u'Username: ')
    pwd = prompt(u'Password: ')
    
    if not Utils.check_user(username, pwd):
        print "Username/Password Entered is wrong"
    else:
        send_telnet_issue_mail():
