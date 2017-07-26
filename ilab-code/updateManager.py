#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

from libilab.Database import *
from subprocess import check_output

if __name__ == '__main__':
    for sw in Switches.select().where(Switches.manager.is_null()):
        insertList = []
        users = str(sw.user).lower().split(',')
        for user in users:
            res = check_output(["/usr/cisco/bin/rchain","-h","-M %s" % (user)]).split()
            if res:
                if str(res[-1]) not in insertList:
                    insertList.append(str(res[-1]))
        sw.manager = ','.join(insertList)
        sw.save()

    for sw in Switches.select().where(Switches.manager!='', Switches.director.is_null()):
        insertList = []
        users = str(sw.user).lower().split(',')
        for user in users:
            res = check_output(["/usr/cisco/bin/rchain","-h","-M %s" % (user)]).split()
            if res:
                if 'joyj' in res:
                    if 'joyj' not in insertList:
                        insertList.append('joyj')
                if 'dkhurana' in res:
                    if 'dkhurana' not in insertList:
                        insertList.append('dkhurana')
                if 'venkat' in res:
                    if 'venkat' not in insertList:
                        insertList.append('venkat')
                if 'jredclif' in res:
                    if 'jredclif' not in insertList:
                        insertList.append('jredclif')
                if 'vparames' in res:
                    if 'vparames' not in insertList:
                        insertList.append('vparames')
                if 'ashokt' in res:
                    if 'ashokt' not in insertList:
                        insertList.append('ashokt')
        sw.director = ','.join(insertList)
        sw.save()
