#!/home/ilab/python2.7.11/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2015  The iLab Development Team
#
#  version = 3.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os, sys, time 
import traceback
import pexpect
import re
import logging
from abc import ABCMeta, abstractmethod

from ilab import *

class Switch(object):
    
    def __init__(self, switch):
        self._id = str(switch['id'])
        self._switch_name = str(switch['switch_name'])
        self._console_ip = str(switch['console_ip'])
        self._mgmt_ip = str(switch['mgmt_ip'])
        self.act_port = str(switch['active_port'])
        self.stnd_port = str(switch['standby_port'])
        self._switch_pwd = str(switch['switch_pwd'])
        self._console_pwd = 'nbv123'
        self._log = "" 
        self.kick = str(switch['kickstart'])
        self.sys = str(switch['system'])

    def __str__(self):
        return "Switch(switch_name=%s, console_ip=%s, mgmt_ip=%s, active_port=%s, standby_port=%s)" \
            % (self.switch_name, self.console_ip, self.mgmt_ip, self.act_port, self.stnd_port)
    
    #### Define the getters and setters ####
    
    # Getter for switch id
    @property
    def id(self):
        return self._id

    # Getter for switch name
    @property
    def switch_name(self):
        return self._switch_name
    
    # Getter for console_ip
    @property
    def console_ip(self):
        return self._console_ip
    
    # Getter for console_ip
    @property
    def mgmt_ip(self):
        return self._mgmt_ip
    
    # Getter/Setter for active port
    @property
    def act_port(self):
        return self._act_port
    
    @act_port.setter
    def act_port(self, port):
        self._act_port = port
    
    # Getter/Setter for standby port
    @property
    def stnd_port(self):
        return self._stnd_port
    
    @stnd_port.setter
    def stnd_port(self, port):
        self._stnd_port = port
    
    # Getter for switch password
    @property
    def switch_pwd(self):
        return self._switch_pwd
    
    # Getter for console password
    @property
    def console_pwd(self):
        return self._console_pwd
    
    # Getter for logging file
    @property
    def log(self):
        return self._log
    
    # Getter/Setter for kickstart image
    @property
    def kick(self):
        return self._kick
    
    @kick.setter
    def kick(self, kick):
        self._kick = kick
    
    # Getter/Setter for system image
    @property
    def sys(self):
        return self._sys
    
    @sys.setter
    def sys(self, sys):
        self._sys = sys
    
    #### End of getters and setters ####

    __metaclass__ = ABCMeta

    @abstractmethod
    def load_or_telnet_image(self, log):
        return
    
    @abstractmethod 
    def copy_images_to_switch(self, log):
        return

    #### Start of Static methods ####

    @staticmethod
    def setip(switch_cons,mgmt_ip):
        switch_cons.sendline('config t');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('interface m0');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('ip address %s/23'%mgmt_ip);
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('no shut');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('exit');
        switch_cons.expect(SWITCH_PROMPT)
        ip=mgmt_ip.split('.')
        switch_cons.sendline('ip route 0.0.0.0/0 %s.%s.%s.1'%(ip[0],ip[1],ip[2]));
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('vrf context management');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('ip route 0.0.0.0/0 %s.%s.%s.1'%(ip[0],ip[1],ip[2]));
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('feature telnet');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('telnet server enable');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('feature scp-server');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('exit');
        switch_cons.expect(SWITCH_PROMPT)
        return

    @staticmethod
    def setip_in_boot(switch_cons,mgmt_ip):
        switch_cons.sendline('config t');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('interface mgmt0');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('ip address %s 255.255.254.0' % mgmt_ip);
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('no shut');
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('exit');
        switch_cons.expect(SWITCH_PROMPT)
        ip=mgmt_ip.split('.')
        switch_cons.sendline('ip default-gateway %s.%s.%s.1'%(ip[0],ip[1],ip[2]));
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('exit')
        switch_cons.expect(SWITCH_PROMPT)
        return

    #Copy the kickstart, System and ascii-replay file to server
    @staticmethod
    def copy_files_to_server(switch_cons,s_file,d_file,pwd='nbv_12345'):
        switch_cons.sendline('copy bootflash:%s scp://ilab@%s/%s/%s vrf management'%(s_file, HOST, data_dir, d_file))
        i = switch_cons.expect([r'yes/no', r'assword:'])
        while i >= 0:
            if i==0:
                switch_cons.sendline('yes')
            if i==1:
                switch_cons.sendline(pwd)
                break
            i = switch_cons.expect([r'yes/no', r'assword:'])
        switch_cons.expect(SWITCH_PROMPT, 600)
        return

    #Copy the kickstart, System and ascii-replay file to switch
    @staticmethod
    def copy_files_to_switch(switch_cons,s_file,d_file,pwd='nbv_12345'):
        switch_cons.sendline('copy scp://ilab@%s/%s/%s bootflash:%s'%(HOST, data_dir, s_file, d_file))
        i = switch_cons.expect([r'yes/no', r'assword:'])
        while i >= 0:
            if i==0:
                switch_cons.sendline('yes')
            if i==1:
                switch_cons.sendline(pwd)
                break
            i = switch_cons.expect([r'yes/no', r'assword:'])
        switch_cons.expect(SWITCH_PROMPT, 600)
        return

    @staticmethod
    def get_switch_module_details_from_mgmt(mgmt_ip, switch_pwd, log):
        xml = {}
        console = pexpect.spawn('telnet -l admin %s' % (mgmt_ip))
        console.logfile = log 
        time.sleep(2)
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, 'assword:', \
                r'Login incorrect', SWITCH_PROMPT], 5)
        while i >= 0:
            if i == 0:
                console.close()
                return "" 
            if i == 1:
                console.close()
                return "" 
            if i == 2:
                console.sendline(switch_pwd)
            if i == 3:
                console.close()
                return ""
            if i == 4:
                break
            i = console.expect([pexpect.TIMEOUT, pexpect.EOF, 'assword:', \
                    r'Login incorrect', SWITCH_PROMPT], 5)
        
        console.sendline('terminal length 0')
        console.expect(SWITCH_PROMPT)
        console.sendline('show inventory | xml')
        console.expect(SWITCH_PROMPT)
        xml['inv'] = console.before
        console.sendline('show system uptime | xml')
        console.expect(SWITCH_PROMPT)
        xml['uptime'] = console.before
        console.close()
        return xml

    @staticmethod
    def get_switch_module_details_from_console(console_ip, port, switch_pwd, log):
        xml = {}
        console = pexpect.spawn('telnet %s %s' % (console_ip, port))
        console.logfile = log 
        time.sleep(2)
        console.sendline('')
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, r'Login incorrect', \
                'ogin:', 'assword:', BASH_SHELL, DEBUG_SHELL, \
                SWITCH_PROMPT], 5)
        while i >= 0:
            if i == 0:
                console.close()
                return "" 
            if i == 1:
                console.close()
                return ""
            if i == 2:
                console.close()
                return ""
            if i == 3:
                console.sendline('admin')
            if i == 4:
                console.sendline(switch_pwd)
            if i == 5 or i == 6:
                console.sendline('exit')
            if i == 7:
                break
            i = console.expect([pexpect.TIMEOUT, pexpect.EOF, r'Login incorrect', \
                    'ogin:', 'assword:', BASH_SHELL, DEBUG_SHELL, \
                    SWITCH_PROMPT], 5)
        
        console.sendline('terminal length 0')
        console.expect(SWITCH_PROMPT)
        console.sendline('show inventory | xml')
        console.expect(SWITCH_PROMPT)
        xml['inv'] = console.before
        console.sendline('show system uptime | xml')
        console.expect(SWITCH_PROMPT)
        xml['uptime'] = console.before
        console.close()
        return xml

    #### End of Static methods ####

    def ascii_load(self,log):
        time.sleep(5*60)
        child = pexpect.spawn('telnet %s %s'%(self.console_ip,self.act_port))
        child.logfile = log
        child.sendline('')
        i = child.expect ([pexpect.TIMEOUT, pexpect.EOF, SWITCH_LOGIN, 'assword:', SWITCH_PROMPT])
        if i==0:
            logging.info(str(child))
            return 
        if i==1:
            logging.info(str(child))
            return
        if i==2:
            child.sendline('admin')
            child.expect ('assword:')
            child.sendline(self.switch_pwd)
            child.expect(SWITCH_PROMPT)
            "Now copy the running ascii file to power_config"
            child.sendline('copy bootflash:run_power_config running-config')
        if i==3:
            child.sendline(self.switch_pwd)
            child.expect(SWITCH_PROMPT)
            "Now copy the startup ascii file to power_config"
            child.sendline('copy bootflash:run_power_config running-config')
        if i==4:
            "Now copy the ascii file to power_config"
            child.sendline('copy bootflash:run_power_config running-config')

        child.sendline('')
        time.sleep(2)
        child.sendline('')
        time.sleep(2)
        child.sendline('')
        time.sleep(2)
        child.sendline('')
        time.sleep(2)
        child.sendline('')
        time.sleep(2)
        
        child.close()
        return True

    def clear_console(self, log):
        """
        Clear telnet console for both active and standby ports
        Telnet handle is closed in function
            # telnet 172.23.152.100 (enter password)
            # en (enter password)
            # clear line 10
            # clear line 11
        """
        allports = [self.act_port, self.stnd_port]
        logging.info("Clearing console with ip=%s and ports=%s", self.console_ip, allports)
        console = pexpect.spawn('telnet %s'%(self.console_ip))
        console.logfile = log
        console.sendline('')
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, 'Password:', CONSOLE_PROMPT, EN_CONSOLE_PROMPT])
        if i == 0:
            logging.debug('TIMEOUT exception. Here is what telnet said:')
            logging.debug(str(console))
            sys.exit (1)
        if i == 1:
            logging.debug('EOF expection. Here is what telnet said:')
            logging.debug(str(console))
            sys.exit (1)
        if i == 2:
            console.sendline(self.console_pwd)
            console.expect(CONSOLE_PROMPT)
            console.sendline('en')
            console.expect('Password:')
            console.sendline(self.console_pwd)
        if i == 3:
            console.sendline('en')
            console.expect('Password:')
            console.sendline(self.console_pwd)
        if i == 4:
            pass
        
        for port in allports:
            if port != '':
                po = int(port)%100
                console.expect(EN_CONSOLE_PROMPT)
                console.sendline('clear line %d'%(po))
                console.sendline('\r')
                console.expect('confirm')
                console.sendline('\r')
        console.expect(EN_CONSOLE_PROMPT)
        console.sendline('exit')
        time.sleep(2)
        console.close()
        return

    def clear_screen(self,log):
        """
        This definitions will clear the switch console and bring it to switch
        prompt
            ....CTRL+C.....
            switch#
        """
        ports = []
        ports.append(self.act_port)
        if self.stnd_port != "":
            ports.append(self.stnd_port)
        
        for port in ports:
            logging.info("Clearing screen for port %s", port)
            console = pexpect.spawn('telnet %s %s'%(self.console_ip,port))
            console.logfile = log
            console.send('\003')
            time.sleep(1)
            console.close()
        return

    def check_standby(self, port, log):
        """
        This definition is to check if the given port is for active sup or standby sup
        Telnet handle is closed in function and returned True or False
            switch(standby) # show vdc
                              ^
            Invalid command....
        """
        logging.info("Checking if port=%s is standby for ip=%s", port, self.console_ip)
        switch = pexpect.spawn('telnet %s %s'%(self.console_ip,port))
        switch.logfile = log
        time.sleep(2)
        switch.sendline('')
        i = switch.expect([pexpect.TIMEOUT, pexpect.EOF, SWITCH_STANDBY, DEBUG_SHELL, BASH_SHELL, \
                SWITCH_PROMPT, SWITCH_LOGIN, 'assword:'], 5)
        while i>=0:
            if i==0:
                logging.info('This is pexpect.TIMEOUT and hence is active return FALSE')
                switch.close()
                return True
            if i==1:
                logging.info('This is pexpect.EOF and hence is standby return true')
                switch.close()
                return True
            if i==2:
                logging.info('Its standby console and hence is standby return true')
                switch.close()
                return True
            if i>2 and i<5:
                logging.info('Its in bash/debug shell so exit and try again')
                switch.sendline('exit')
            if i==5:
                switch.send('\003')
                switch.expect(SWITCH_PROMPT)
                switch.sendline('switchback')
                switch.expect(SWITCH_PROMPT)
                switch.sendline('show vdc')
                switch.expect(SWITCH_PROMPT)
                text = switch.before
                stmnt = 'Switchwide mode is'
                if stmnt in text:
                    switch.close()
                    return False
                else:
                    switch.close()
                    return True
            if i==6:
                switch.sendline('admin')
            if i==7:
                switch.sendline(self.switch_pwd)
            i = switch.expect([pexpect.TIMEOUT, pexpect.EOF, SWITCH_STANDBY, DEBUG_SHELL, BASH_SHELL, \
                    SWITCH_PROMPT, SWITCH_LOGIN, 'assword:'], 5)
        
        switch.close()
        return True
    
    def check_any_logged_user(self, log):
        """
        Check if the user is logged into the system. For this switch ip needs
        to be set else it will not work.
            switch# bash
            (none)(shell)> who
            admin    ttyS0        Oct 11 03:58
            admin    pts/0        Oct 11 04:01 (10.21.31.111)
            (none)(shell)>
        This above example shows there are 2 users logged into as admin.
        """
        console = pexpect.spawn('ssh admin@%s' % (self.console_ip))
        console.logfile = log
        time.sleep(2)
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, SWITCH_LOGIN, 'Password:', SWITCH_PROMPT])
        if i == 0:
            return False 
        if i == 1:
            return False 
        if i == 2:
            console.sendline('admin')
            console.expect('Password:')
            console.sendline(self.switch_pwd)
        if i == 3:
            console.sendline(self.switch_pwd)
        if i == 4:
            pass

        console.expect(SWITCH_PROMPT)
        console.sendline('bash')
        console.expect(BASH_SHELL)
        console.sendline('who')
        console.expect(BASH_SHELL)
        details = console.before
        if details.count('admin') > 1:
            console.close()
            return True
        else: 
            console.close()
            return False

    def get_switch_module_details(self, log):
        """
        This function will retrieve the "show module | xml" details into a
        xml format which inturn will be returned to the caller
        """
        logging.info("Logging into switch %s to collect details", self.switch_name)
        xml = {}
        xml['mgmt_issue'] = False
        xml['telnet_issue'] = False
        xml['output'] = ""
        xml['uptime'] = ""

        output = Switch.get_switch_module_details_from_mgmt(self.mgmt_ip, self.switch_pwd, log)
        if output == "":
            xml['mgmt_issue'] = True 
            #Always Clear the Consoles while working on the console
            self.clear_console(log)
            self.clear_screen(log)
            #Check which port is active one
            if str(self.stnd_port) != '':
                ports = [self.act_port, self.stnd_port]
                checkpo0 = self.check_standby(ports[0],log)
                checkpo1 = self.check_standby(ports[1],log)
                if not(checkpo0) and not(checkpo1):
                    st_port = ports[1]
                    port = ports[0]
                if checkpo0:
                    st_port = ports[0]
                    port = ports[1]
                if checkpo1:
                    st_port = ports[1]
                    port = ports[0]
                self.act_port = port
                self.stnd_port = st_port
            output = Switch.get_switch_module_details_from_console(self.console_ip, \
                                self.act_port, self.switch_pwd, log)
            if output == "":
                xml['telnet_issue'] = True 
        if output:
            xml['output'],xml['uptime'] = output.values()
        return xml
