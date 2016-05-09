#!/ws/rkorlepa-sjc/python/bin/python

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
