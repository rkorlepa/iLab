#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os
import re
import logging
from subprocess import call, check_output
from prompt_toolkit import prompt

from libilab import *
from libilab.Exceptions import *
from libilab.Database import *
from libilab.Utils import Utils

from Utils import swUtils

if __name__ == "__main__":

    print " 1. Get the details of switches\n 2. Send mail to users about the telnet issue\n 3. Send mail to users about the passowd issue\n"
    whattodo = prompt(u'Select the option you would like to perform [1,2,3]: ')
    whattodo = int(whattodo)

    if whattodo != 1 and whattodo != 2 and whattodo != 3:
        print "The option doesn't exist, Please try again"
        sys.exit(1)

    if whattodo == 1:
        print "Sit back and relax will take some time..."
        print "(DO NOT CTRL+C)"
        strfile = '%s/sw_details.log' % os.getcwd() 
        cli_cmd = 'rm %s' % (strfile)
        call(cli_cmd, shell=True)
        fout = None
        #fout = file(strfile, 'a')
        logging.basicConfig(filename=strfile, format='%(asctime)s: %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

        print " 1. Fetch details based on user ids\n 2. Fetch details based on switch type\n"
        temp_whattodo = prompt(u'Select the option you would like to perform [1,2]: ')
        temp_whattodo = int(temp_whattodo)
        
        if whattodo != 1 and whattodo != 2 and whattodo != 3:
            print "The option doesn't exist, Please try again"
            sys.exit(1)
        
        if temp_whattodo == 1:
            search_users = prompt(u'Get Details for DUTs under user(comma seperated users): ').split(',')
            using = prompt(u'Get Details using ssh only [y|n]: ')
            count = 0
            for search_user in search_users:
                all_users = check_output(['/usr/cisco/bin/rchain','-R','-h \
                        %s'%str(search_user)]).split()
                for user in all_users:
                    for switch in Switches.select().where(Switches.user==user).dicts():
                        count = count + 1
                        switchId = str(switch['id'])
                        swUtils.switch_details.delay(switchId, fout, str(using).lower())

        if temp_whattodo == 2:
            search_types = prompt(u'Get Details for DUTs of type [n9k, fretta, n7k, xbow, n6k, n5k]: ').split(',')
            using = prompt(u'Get Details using ssh only [y|n]: ')
            count = 0
            for s_type in search_types:
                for switch in Switches.select().where(Switches.switch_type==str(s_type)).dicts():
                    count = count + 1
                    switchId = str(switch['id'])
                    swUtils.switch_details.delay(switchId, fout, str(using).lower())
        print "Collected all the Current Details of %s switches" % count

    if whattodo == 2:
        username = prompt(u'Username: ')
        pwd = prompt(u'Password: ')
        swtype = prompt(u'Query for switch_type (n9k,fretta,n7k,xbow,n6k,n5k): ')
        
        if not Utils.check_user(username, pwd):
            print "Username/Password Entered is wrong"
        else:
            print "\nSending Mail to users with telnet/mgmt issue\n"
            swUtils.send_telnet_issue_mail(str(swtype))

    if whattodo == 3:
        username = prompt(u'Username: ')
        pwd = prompt(u'Password: ')
        swtype = prompt(u'Query for switch_type (n9k,fretta,n7k,xbow,n6k,n5k): ')

        if not Utils.check_user(username, pwd):
            print "Username/Password Entered is wrong"
        else:
            print "\nSending Mail to users with password issue\n"
            swUtils.send_pwd_issue_mail(str(swtype))
