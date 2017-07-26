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

from libilab import *
from libilab.Exceptions import *
from libilab.Utils import Utils

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
        self._console_user = str(switch['console_login']).split(':')[0]
        self._console_pwd = str(switch['console_login']).split(':')[1]
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
    
    # Getter for console user 
    @property
    def console_user(self):
        return self._console_user


    # Getter/Setter for active port
    @property
    def console_pwd(self):
        return self._console_pwd
    
    @console_pwd.setter
    def console_pwd(self, console_pwd):
        self._console_pwd = console_pwd
    
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
        """
        This is the function which will clear console port
        There is special functionality which will detect and update the pwd of
        the telnet console if user has given a wrong one.
        It will try only nbv123, lab, cisco123 as these are the common ones
        used in lab and also since we have only 3 tries.
        """
        logging.info("Clearing console with ip=%s and ports=%s", console_ip, port)
        pwdList = ['cisco123', 'lab', 'nbv123']
        pwdList.remove(self.console_pwd)
        pwdTry = 0
        console = pexpect.spawn('telnet %s'%(console_ip))
        console.logfile = self.log
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, r'Bad', r'(?i)incorrect',  PWD_PROMPT, CONSOLE_PROMPT, EN_CONSOLE_PROMPT], 5)
        while i >= 0:
            if i == 0:
                console.close()
                raise TimeoutError('Clear Console Timeout error')
            if i == 1:
                console.close()
                raise EofError('Clear Console EOF error')
            if i == 2 or i == 3:
                console.close()
                raise PasswordError('Clear Console, Password error')
            if i == 4:
                logging.info("pwd %s", self.console_pwd)
                if pwdTry == 0:
                    console.sendline(self.console_pwd)
                elif pwdTry > 0 and pwdTry <= len(pwdList):
                    console.sendline(pwdList[pwdTry - 1])
                    self.console_pwd = pwdList[pwdTry-1]
                else:
                    console.close()
                    raise PasswordError('Clear Console, Password error')
                pwdTry = pwdTry + 1
            if i == 5:
                logging.info("console prompt")
                Utils.update_console_login_details(self.switch_name, self.console_user, self.console_pwd)
                console.sendline('en')
                console.expect(PWD_PROMPT)
                console.sendline(self.console_pwd)
            if i == 6:
                logging.info("en console prompt")
                Utils.update_console_login_details(self.switch_name, self.console_user, self.console_pwd)
                break 
            i = console.expect([pexpect.TIMEOUT, pexpect.EOF, r'Bad', r'(?i)incorrect',  PWD_PROMPT, CONSOLE_PROMPT, EN_CONSOLE_PROMPT], 5)
        
        po = int(port)%100
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
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, \
                AUTH_ISSUE, LOADER_PROMPT, BOOT_PROMPT, SSH_NEWKEY, \
                PWD_PROMPT, SWITCH_PROMPT], 5)
        while i >= 0:
            if i == 0:
                console.close()
                logging.info('connect_mgmt_ip, Timed out, Not able to access mgmt for (%s)', self.switch_name)
                raise TimeoutError('connect_mgmt_ip, Timed out, Not able to access mgmt')
            if i == 1:
                console.close()
                logging.info('connect_mgmt_ip, Eof error, Not able to access mgmt for (%s)', self.switch_name)
                raise EofError('connect_mgmt_ip, Eof error, Not able to access mgmt')
            if i == 2 or i == 3:
                console.close()
                logging.info('connect_mgmt_ip, Password error')
                raise PasswordError('connect_mgmt_ip, Password error')
            if i == 4 or i == 5:
                console.close()
                logging.info('connect_mgmt_ip, Switch in loader/boot prompt')
                raise LoaderError('connect_mgmt_ip, Switch in loader/boot prompt')
            if i == 6:
                console.sendline('yes')
            if i == 7:
                console.sendline(self.switch_pwd)
            if i == 8:
                break
            i = console.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, \
                    AUTH_ISSUE, LOADER_PROMPT, BOOT_PROMPT, SSH_NEWKEY, \
                    PWD_PROMPT, SWITCH_PROMPT], 5)

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
        console.sendline('')
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, \
            'Abort Auto Provisioning and continue.*', 'enable admin vdc.*', \
            'enforce secure password.*', 'the basic configuration dialog.*', \
            'the password for.*', LOADER_PROMPT, BOOT_PROMPT, BASH_SHELL, DEBUG_SHELL, \
            SWITCH_LOGIN, PWD_PROMPT, SWITCH_PROMPT])
        while i >= 0:
            if i == 0:
                console.close()
                logging.info('telnet_console_port, Timed out, Not able to access console')
                raise TimeoutError('telnet_console_port, Timed out, Not able to access console')
            if i == 1:
                console.close()
                logging.info('telnet_console_port, Eof error, Not able to access console')
                raise EofError('telnet_console_port, Eof error, Not able to access console')
            if i == 2:
                console.close()
                logging.info('telnet_console_port, Password error')
                raise PasswordError('telnet_console_port, Password error')
            if i>2 and i<8:
                console.close()
                logging.info("telnet_console_port, switch is booting so load and check")
                raise BootingError("telnet_console_port, switch is booting so load and check")
            if i == 8 or i == 9:
                console.close()
                logging.info('telnet_console_port, Switch in loader/boot prompt')
                raise LoaderError('telnet_console_port, Switch in loader/boot prompt')
            if i == 10 or i == 11:
                console.sendline('exit')
            if i == 12:
                console.sendline('admin')
            if i == 13:
                console.sendline(self.switch_pwd)
            if i == 14:
                break
            i = console.expect([pexpect.TIMEOUT, pexpect.EOF, LOGIN_INCORRECT, \
                'Abort Auto Provisioning and continue.*', 'enable admin vdc.*', \
                'enforce secure password.*', 'the basic configuration dialog.*', \
                'the password for.*', LOADER_PROMPT, BOOT_PROMPT, BASH_SHELL, DEBUG_SHELL, \
                SWITCH_LOGIN, PWD_PROMPT, SWITCH_PROMPT], 5)
        
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
        logging.info('done clear screen') 
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
        switch.send('\003')
        switch.sendline('')
        switch.send('\003')
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
        console = self.connect_mgmt_ip(using)
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
        console.expect(SWITCH_PROMPT,120)
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
        console.expect(SWITCH_PROMPT,120)
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
