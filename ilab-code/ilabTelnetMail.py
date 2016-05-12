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

if __name__ == '__main__':
    pwdIssue = defaultdict(list)
    for sw_st in Switch_Status.select(Switch_Status.id,Switch_Status.switch_name).where(Switch_Status.telnet_issue==1):
        user = Switches.get(Switches.id == sw_st.id).user
        pwdIssue[str(user)].append(str(sw_st.switch_name))
    for key,value in pwdIssue.items():
        user = str(key)
        duts = ', '.join(value)
        pwd_template = ilab_template("detailsIncorrect.txt").render(user=user, \
                switch_names=duts)
        from_list = to_list = user + "@cisco.com"
        mailer = IlabEmail(from_list, to_list)
        subject = "iLab[ISSUE] Incorrect Password in iLab DB"
        mailer.set_subject(subject)
        mailer.add_line(pwd_template)
        mailer.send()
        mailer.reset()
        print "Mail sent to %s for duts %s" % (user, duts)
