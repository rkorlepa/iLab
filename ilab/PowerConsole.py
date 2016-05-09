#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os, sys, time 
import traceback
import pexpect
import re
import logging
import telnetlib

from ilab import *

class Power(object):

    def __init__(self, power_console_detail):
        consoles = power_console_detail.split('|')
        dicts = {}
        for console in consoles:
            temp = console.split(':')
            tempOutlets = temp[1].split(',')
            dicts[temp[0]] = (tempOutlets, temp[2], temp[3])
        self._power_dict = dicts

    #### Define the getters and setters ####

    # Getter for power dictionary which has {'172.23.152.111' -> ('11,12','nbv123')} 
    @property
    def power_dict(self):
        return self._power_dict

    #### End of getters and setters ####
    
    def __power_on_off_px2_pdu_console(self, ip, outlets, user, pwd, whatToDo, log):
        """
        Power off PDU console only for apc check next function
            # power outlets 11 on
            Do you wish to turn outlet 11 on? [y/n] y
            # power outlets 20 on
            Do you wish to turn outlet 20 on? [y/n] y
            # exit
        Telnet handle is closed in the function
        """
        logging.info("Power %s switch ip %s with outlets %s for PDU PX2", whatToDo, ip, outlets)
        child = pexpect.spawn('telnet %s'%(ip))
        child.logfile = log
        time.sleep(3)
        i = child.expect ([pexpect.TIMEOUT, pexpect.EOF, 'Username:', 'assword:'])
        if i == 0:
            logging.debug('TIMEOUT exception. Here is what telnet said:')
            logging.debug(str(child))
            sys.exit (1)
        if i == 1:
            logging.debug('EOF expection. Here is what telnet said:')
            logging.debug(str(child))
            sys.exit (1)
        if i == 2:
            child.sendline(str(user))
            child.expect('P|password')
            child.sendline(pwd)
            child.expect(POWER_PROMPT)
        if i == 3:
            child.sendline(pwd)
            child.expect(POWER_PROMPT)
            pass
        
        for out in outlets:
            child.sendline('power outlets %s %s'%(out, whatToDo))
            time.sleep(1)
            child.expect('[y/n]')
            time.sleep(1)
            child.sendline('y')
            child.expect(POWER_PROMPT)
        child.sendline('exit')
        child.close()
        return

    def __power_on_off_px_pdu_console(self, ip, outlets, user, pwd, whatToDo, log):
        """
        Power off PDU console only for apc check next function
            # set /system1/outlet10 powerState=on
            /system1/outlet1
             Properties:
               Name is OUTLET10
               powerState is 10 (on)
            # set /system1/outlet20 powerState=on
            /system1/outlet1
             Properties:
               Name is OUTLET20
               powerState is 20 (on)
            # exit
        Telnet handle is closed in the function
        """
        logging.info("Power %s switch ip %s with outlets %s for PDU PX", whatToDo, ip, outlets)
        tn = telnetlib.Telnet(ip)
        
        tn.read_until("Login:")
        tn.write(str(user) + "\r")
        time.sleep(1)
        tn.read_until("Password:")
        tn.write(str(pwd) + "\r")
        time.sleep(1)

        for out in outlets:
            cli = 'set /system1/outlet%s powerState=%s'%(out, whatToDo)
            tn.write(cli + "\r")
            time.sleep(1)

        output=tn.read_very_eager()
        tn.close()
        logging.info("%s", output)
        return

    def __power_on_off_apc_console(self, ip, outlets, user, pwd, whatToDo, log):
        """
        Power On/Off APC console, use the upper definition if raritran power
        console
        """
        logging.info("Power %s switch ip %s with outlets %s for PDU APC", whatToDo, ip, outlets)
        tn = telnetlib.Telnet(ip)

        tn.read_until("Name ")
        tn.write(str(user) + "\r")
        time.sleep(1)
        tn.read_until("Password ")
        tn.write(str(pwd) + "\r")
        time.sleep(1)

        tn.write("1" + "\r")
        time.sleep(1)
        tn.write("2" + "\r")
        time.sleep(1)
        tn.write("1" + "\r")
        time.sleep(1)
        tn.write("" + "\r")
        time.sleep(1)

        for out in outlets:
            tn.write(str(out) + "\r")   #This is the outlet to specify for power on/off
            time.sleep(1)
            tn.write("1" + "\r")
            time.sleep(1)
            if whatToDo.lower() == 'off':
                tn.write("2" + "\r")   #This is the one to specify for ON=1 or OFF=2
            else:
                tn.write("1" + "\r")   #This is the one to specify for ON=1 or OFF=2
            time.sleep(1)
            tn.write("YES" + "\r")
            time.sleep(1)
            tn.write("" + "\r")
            time.sleep(1)
            tn.write("\x1b")
            time.sleep(1)
            tn.write("\x1b")
            time.sleep(1)
            tn.write("" + "\r")
            time.sleep(1)

        tn.write("\x1b")
        time.sleep(1)
        tn.write("\x1b")
        time.sleep(1)
        tn.write("\x1b")
        time.sleep(1)
        tn.write("4" + "\r")
        time.sleep(1)

        output=tn.read_very_eager()
        tn.close()
        logging.info("%s", output)
        return

    def power_console_on_off(self, whatToDo, log):
        """
        This function will find which kind of console it is and save it in
        database for later use. There are 3 type currently in our labs and
        more can be added based on requirement. For every power unit different
        clis are used to power off/on and hence different implementations.
        1. PDU - PX2 CLI
        2. APC - NONE
        3. PDU - PX CLP
        """
        logging.info("Checking the type of PDU with details as %s" % (self.power_dict))
        for pip,details in self.power_dict.items():
            child = pexpect.spawn('telnet %s' % pip)
            child.logfile = log
            child.expect([':'])
            loginOutput = child.before
            child.sendcontrol(']')
            child.expect('telnet>')
            child.sendline('q')
            time.sleep(1)
            child.expect('Connection')
            child.close()
            if 'PX2 CLI' in loginOutput:
                self.__power_on_off_px2_pdu_console(pip, details[0], details[1], details[2], whatToDo, log)
            elif 'PX CLP' in loginOutput:
                self.__power_on_off_px_pdu_console(pip, details[0], details[1], details[2], whatToDo, log)
            else:
                self.__power_on_off_apc_console(pip, details[0], details[1], details[2],  whatToDo, log)
                
        return
