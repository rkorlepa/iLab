#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

from collections import defaultdict
from prompt_toolkit import prompt

from ilab import *
from ilab.Database import *
from ilab.ilabmail import *
from ilab.Utils import *

def send_pwd_issue_mail(userty):
    pwdIssue = defaultdict(list)
    for sw_st in Switch_Status.select(Switch_Status.id,Switch_Status.switch_name).\
                    where(Switch_Status.password_issue==1, Switch_Status.user==userty):
        user = Switches.get(Switches.id == sw_st.id).user
        pwdIssue[str(user)].append(str(sw_st.switch_name))
    for key,value in pwdIssue.items():
        user = str(key)
        duts = ', '.join(value)
        pwd_template = ilab_template("pwdIncorrect.txt").render(user=user, \
                switch_names=duts)
        from_list = "jaipatel@cisco.com"
        to_list = user + "@cisco.com"
        mailer = IlabEmail(from_list, to_list)
        subject = "iLab[ISSUE] Incorrect Password in iLab DB"
        mailer.set_subject(subject)
        mailer.add_line(pwd_template)
        mailer.send()
        mailer.reset()
        print "Mail sent to %s for duts %s" % (user, duts)

if __name__ == '__main__':
    username = prompt(u'Username: ')
    pwd = prompt(u'Password: ')
    userty = prompt(u'Which type of User(dev/qa):')

    if not Utils.check_user(username, pwd):
        print "Username/Password Entered is wrong"
    else:
        if str(userty).lower() != "dev" and str(userty).lower() != "qa":
            print "Only Accepted values are dev/qa for user type"
            sys.exit(0)
        send_pwd_issue_mail(str(userty).upper())
