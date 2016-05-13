#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

from ilab.Database import *
from subprocess import check_output

if __name__ == '__main__':
    for sw in Switches.select().where(Switches.manager==''):
        insertList = []
        users = str(sw.user).lower().split(',')
        for user in users:
            res = check_output(["/usr/cisco/bin/rchain","-h","-M %s" % (user)]).split()
            if res:
                if str(res[-1]) not in insertList:
                    insertList.append(str(res[-1]))
        sw.manager = ','.join(insertList)
        sw.save()
