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
from abc import ABCMeta, abstractmethod

from ilab import *
from ilab.Exceptions import *
from ilab.Utils import Utils

class Switch(object):
    
    def __init__(self, switch):
        self._id = str(switch['id'])
        self._switch_name = str(switch['switch_name'])
        self.console_ip = str(switch['console_ip'])
        self._mgmt_ip = str(switch['mgmt_ip']) if switch['mgmt_ip'] else None
        self.act_port = str(switch['active_port'])
        self.stnd_console_ip = str(switch['stnd_console_ip']) if switch['stnd_console_ip'] else None
        self.stnd_port = str(switch['standby_port']) if switch['standby_port'] else None
        self._switch_pwd = str(switch['switch_pwd'])
        self._console_pwd = 'nbv123'
        self.log = None 
        self.kick = str(switch['kickstart']) if switch['kickstart'] else None
        self.sys = str(switch['system']) if switch['system'] else None

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
    
    # Getter/Setter for console_ip
    @property
    def console_ip(self):
        return self._console_ip
    
    @console_ip.setter
    def console_ip(self, console_ip):
        self._console_ip = console_ip
    
    # Getter for mgmt_ip
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
    
    # Getter/Setter for stnd_console_ip
    @property
    def stnd_console_ip(self):
        return self._stnd_console_ip
    
    @stnd_console_ip.setter
    def stnd_console_ip(self, stnd_console_ip):
        self._stnd_console_ip = stnd_console_ip
    
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
    
    @log.setter
    def log(self, log):
        self._log = log

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
    def load_image_using_telnet(self):
        return
    
    @abstractmethod 
    def copy_images_to_switch(self):
        return

    #### Start of Private methods ####
    
    def __clear_telnet_port(self, console_ip, port):
        logging.info("Clearing console with ip=%s and ports=%s", console_ip, port)
        console = pexpect.spawn('telnet %s'%(console_ip))
        console.logfile = self.log
        console.sendline('')
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, PWD_PROMPT, CONSOLE_PROMPT, EN_CONSOLE_PROMPT], 5)
        if i == 0:
            raise TimeoutError('Clear Console Timeout error')
        if i == 1:
            raise EofError('Clear Console EOF error')
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
        
        po = int(port)%100
        console.expect(EN_CONSOLE_PROMPT)
        console.sendline('clear line %d'%(po))
        console.sendline('\r')
        console.expect('confirm')
        console.sendline('\r')
        console.expect(EN_CONSOLE_PROMPT)
        console.sendline('exit')
        time.sleep(1)
        console.close()
        return

    #### End of Private methods ####
    
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

    #### End of Static methods ####

    def connect_mgmt_ip(self, using):
        """
        This definition will telnet/ssh to the active sup mgmt ip provided 
        in the switch object (Default is ssh)
        [IMP]Telnet handle and needs to be closed by client

            Eg: testuser[13:00:00]> ssh admin@111.111.111.111
               or
                testuser[13:00:00]> telnet -l admin 111.111.111.111
        """
        if using == 'ssh':
            logging.info('Trying to ssh to mgmt ip %s', self.mgmt_ip)
            Utils.remove_known_hosts(self.mgmt_ip)
            console = pexpect.spawn('ssh admin@%s' % (self.mgmt_ip))
        else:
            logging.info('Trying to telnet to mgmt ip %s', self.mgmt_ip)
            console = pexpect.spawn('telnet -l admin %s' % (self.mgmt_ip))
        console.logfile = self.log
        time.sleep(2)
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, \
                AUTH_ISSUE, LOADER_PROMPT, BOOT_PROMPT, PWD_PROMPT, SWITCH_PROMPT], 5)
        while i >= 0:
            if i == 0:
                console.close()
                logging.info('get_switch_module_details_from_mgmt, Timed out, Not able to access mgmt')
                raise TimeoutError('get_switch_module_details_from_mgmt, Timed out, Not able to access mgmt')
            if i == 1:
                console.close()
                logging.info('get_switch_module_details_from_mgmt, Eof error, Not able to access mgmt')
                raise EofError('get_switch_module_details_from_mgmt, Eof error, Not able to access mgmt')
            if i == 2 or i == 3:
                console.close()
                logging.info('get_switch_module_details_from_mgmt, Password error')
                raise PasswordError('get_switch_module_details_from_mgmt, Password error')
            if i == 2 or i == 3:
                console.close()
                logging.info('get_switch_module_details_from_mgmt, Switch in loader/boot prompt')
                raise LoaderError('get_switch_module_details_from_mgmt, Switch in loader/boot prompt')
            if i == 6:
                console.sendline(self.switch_pwd)
            if i == 7:
                break
            i = console.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, \
                    AUTH_ISSUE, LOADER_PROMPT, BOOT_PROMPT, PWD_PROMPT, SWITCH_PROMPT], 5)

        return console

    def telnet_console_port(self):
        """
        This definition will telnet to the active sup console port
        provided in the switch object
        [IMP]Telnet handle and needs to be closed by client

            Eg: testuser[13:00:00]> telnet 111.111.111.111 2222
        """
        logging.info('Telnet to console port with ip %s and port %s',self.console_ip, self.act_port)
        console = pexpect.spawn('telnet %s %s' % (self.console_ip, self.act_port))
        console.logfile = self.log 
        time.sleep(2)
        console.sendline('')
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, \
                LOADER_PROMPT, BOOT_PROMPT, BASH_SHELL, DEBUG_SHELL, \
                'ogin:', PWD_PROMPT, SWITCH_PROMPT], 5)
        while i >= 0:
            if i == 0:
                console.close()
                logging.info('get_switch_module_details_from_console, Timed out, Not able to access mgmt')
                raise TimeoutError('get_switch_module_details_from_console, Timed out, Not able to access mgmt')
            if i == 1:
                console.close()
                logging.info('get_switch_module_details_from_console, Eof error, Not able to access mgmt')
                raise EofError('get_switch_module_details_from_console, Eof error, Not able to access mgmt')
            if i == 2:
                console.close()
                logging.info('get_switch_module_details_from_console, Password error')
                raise PasswordError('get_switch_module_details_from_console, Password error')
            if i == 3 or i == 4:
                console.close()
                logging.info('get_switch_module_details_from_console, Switch in loader/boot prompt')
                raise LoaderError('get_switch_module_details_from_console, Switch in loader/boot prompt')
            if i == 5 or i == 6:
                console.sendline('exit')
            if i == 7:
                console.sendline('admin')
            if i == 8:
                console.sendline(self.switch_pwd)
            if i == 9:
                break
            i = console.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, \
                    LOADER_PROMPT, BOOT_PROMPT, BASH_SHELL, DEBUG_SHELL, \
                    'ogin:', PWD_PROMPT, SWITCH_PROMPT], 5)
        
        return console

    def clear_console(self):
        """
        Clear telnet console for both active and standby ports
        [IMP]Telnet handle is closed in function

            # telnet 172.23.152.100 (enter password)
            # en (enter password)
            # clear line 10
            # clear line 11
        """
        try:
            self.__clear_telnet_port(self.console_ip, self.act_port)
            if self.stnd_port and self.stnd_console_ip:
                self.__clear_telnet_port(self.stnd_console_ip, self.stnd_port)
        except:
            logging.info("Some issue in clearing console")
        return

    def clear_screen(self):
        """
        This definitions will clear the switch console and bring it to switch
        prompt
            ....CTRL+C.....
            switch#
        """
        logging.info("Clearing screen for console_ip %s port %s", self.console_ip, self.act_port)
        console = pexpect.spawn('telnet %s %s'%(self.console_ip,self.act_port))
        console.logfile = self.log
        console.send('\003')
        console.close()
        
        if self.stnd_port and self.stnd_console_ip:
            logging.info("Clearing screen for console_ip %s port %s", self.stnd_console_ip, self.stnd_port)
            console = pexpect.spawn('telnet %s %s'%(self.stnd_console_ip,self.stnd_port))
            console.logfile = self.log
            console.send('\003')
            console.close()
        return

    def check_standby(self, console_ip, port):
        """
        This definition is to check if the given port is for active sup or standby sup
        [IMP]Telnet handle is closed in function and returned True or False

            switch(standby) # show vdc
                              ^
            Invalid command....
        """
        logging.info("Checking if port=%s is standby for ip=%s", port, console_ip)
        switch = pexpect.spawn('telnet %s %s'%(console_ip,port))
        switch.logfile = self.log
        switch.sendline('')
        i = switch.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, SWITCH_STANDBY, \
                DEBUG_SHELL, BASH_SHELL, SWITCH_PROMPT, SWITCH_LOGIN, PWD_PROMPT], 5)
        while i>=0:
            if i==0:
                logging.info('This is pexpect.TIMEOUT and hence is standby return true')
                switch.close()
                return True
            if i==1:
                logging.info('This is pexpect.EOF and hence is standby return true')
                switch.close()
                return True
            if i==2:
                logging.info('This is wrong password and hence is standby return true')
                switch.close()
                return True
            if i==3:
                logging.info('Its standby console and hence is standby return true')
                switch.close()
                return True
            if i>3 and i<6:
                logging.info('Its in bash/debug shell so exit and try again')
                switch.sendline('exit')
            if i==6:
                switch.sendline('terminal length 0')
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
            if i==7:
                switch.sendline('admin')
            if i==8:
                switch.sendline(self.switch_pwd)
            i = switch.expect([pexpect.TIMEOUT, pexpect.EOF, r'Login incorrect', SWITCH_STANDBY, \
                    DEBUG_SHELL, BASH_SHELL, SWITCH_PROMPT, SWITCH_LOGIN, PWD_PROMPT], 5)
        
        switch.close()
        return True

    def get_switch_details_from_mgmt(self, using):
        """
        This method will get the inventory details using the active sup mgmt 
        ip using telnet or ssh provided by client (Default is telnet)
        [IMP]Telnet handle is closed in the function

        Details collected are store in dictionary as:
            ret_output['inv'] = show inventory | xml
            ret_output['uptime'] = show system uptime | xml
            ret_output['idletime'] = show accounting log | grep "configure" | last 1
            ret_output['clock'] = show clock | last 1
        """
        ret_output = {}
        #Get the console mgmt handle
        console = self.connect_mgmt_ip("ssh")
        console.sendline('terminal length 0')
        console.expect(SWITCH_PROMPT)
        console.sendline('show inventory | xml')
        console.expect(SWITCH_PROMPT)
        if any(i in console.before for i in INVALID_CLI): raise InvalidCliError('show cmd failure') 
        ret_output['inv'] = console.before
        console.sendline('show system uptime | xml')
        console.expect(SWITCH_PROMPT)
        if any(i in console.before for i in INVALID_CLI): raise InvalidCliError('show cmd failure') 
        ret_output['uptime'] = console.before
        console.sendline('show accounting log | grep "configure" | last 1')
        console.expect(SWITCH_PROMPT)
        if any(i in console.before for i in INVALID_CLI): raise InvalidCliError('show cmd failure') 
        ret_output['idletime'] = console.before
        console.sendline('terminal length 15')
        console.expect(SWITCH_PROMPT)
        console.sendline('show clock | last 1')
        console.expect(SWITCH_PROMPT)
        if any(i in console.before for i in INVALID_CLI): raise InvalidCliError('show cmd failure') 
        ret_output['clock'] = console.before
        console.close()
        return ret_output 

    def get_switch_details_from_console(self):
        """
        This method will get the inventory details using the active sup console
        ip and port.
        [IMP]Telnet handle is closed in the function

        Details collected are store in dictionary as:
            ret_output['inv'] = show inventory | xml
            ret_output['uptime'] = show system uptime | xml
            ret_output['idletime'] = show accounting log | grep "configure" | last 1
            ret_output['clock'] = show clock | last 1
        """
        ret_output = {}
        #Get the console port
        console = self.telnet_console_port()
        console.sendline('terminal length 0')
        console.expect(SWITCH_PROMPT)
        console.sendline('show inventory | xml')
        console.expect(SWITCH_PROMPT)
        if any(i in console.before for i in INVALID_CLI): raise InvalidCliError('show cmd failure') 
        ret_output['inv'] = console.before
        console.sendline('show system uptime | xml')
        console.expect(SWITCH_PROMPT)
        if any(i in console.before for i in INVALID_CLI): raise InvalidCliError('show cmd failure') 
        ret_output['uptime'] = console.before
        console.sendline('show accounting log | grep "configure" | last 1')
        console.expect(SWITCH_PROMPT)
        if any(i in console.before for i in INVALID_CLI): raise InvalidCliError('show cmd failure') 
        ret_output['idletime'] = console.before
        console.sendline('terminal length 15')
        console.expect(SWITCH_PROMPT)
        console.sendline('show clock | last 1')
        console.expect(SWITCH_PROMPT)
        if any(i in console.before for i in INVALID_CLI): raise InvalidCliError('show cmd failure') 
        ret_output['clock'] = console.before
        console.close()
        return ret_output