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
import collections
from abc import ABCMeta, abstractmethod

from libilab import *
from libilab.Switch import Switch 
from libilab.Utils import Utils
from libilab.Exceptions import *

class n89kSwitch(Switch):
    
    def __init__(self, switch):
        Switch.__init__(self, switch)

    #### Define the getters and setters ####
    
    #### End of getters and setters ####
    
    # Definitions of switch functions like below;
    # Clearing consoles, loading image or telnet to a switch, setting ip for switch, 
   
    #### Start of Static methods ####

    @staticmethod 
    def get_images_in_switch(dirs):
        strs = dirs.split()
        images = []
        for s in strs:
            m1 = re.match(r'n9.*dk9([0-9A-Za-z\.]+)', s)
            if m1: 
                images.append(s)
        return images

    #### End of Static methods ####

    def load_image_using_telnet(self):
        """
        This definition is to load the images from loader prompt
        Telnet handle is not closed in function needs to be handled by the caller
            loader> boot <system> (set password and get to loader prompt)
        If already at switch prompt just return the telnet handle
        """
        logging.info("Loading or Telnet to ip=%s with port=%s with sys=%s",self.console_ip,self.act_port,self.sys)
        TIMEOUT = 30
        child = pexpect.spawn('telnet %s %s'%(self.console_ip,self.act_port))
        child.logfile = self.log
        child.sendline('')
        time.sleep(3)
        i = child.expect([pexpect.TIMEOUT, pexpect.EOF, r'Invalid admin', r'Wrong Password', 'loader>.*', \
                'Booting kickstart image:', 'Checking all filesystems', 'INIT: Entering runlevel', \
                'Abort Auto Provisioning and continue.*', 'enable admin vdc.*', 'enforce secure password.*', \
                'the basic configuration dialog.*', 'the password for.*', SWITCH_LOGIN, PWD_PROMPT, \
                BASH_SHELL, DEBUG_SHELL, 'wish to continue:', r'switch.boot.#',  SWITCH_PROMPT], timeout=TIMEOUT)
        while i>=0:
            if i==0:
                TIMEOUT=30
                logging.debug('TIMEOUT exception. Here is what telnet said:')
                logging.debug(str(child))
                child.close()
                raise TimeoutError('load_image_using_telnet, timed out')
            if i==1:
                TIMEOUT=30
                logging.debug('TIMEOUT exception. Here is what telnet said:')
                logging.debug(str(child))
                child.close()
                raise EofError('load_image_using_telnet, eof error')
            if i == 2 or i == 3:
                logging.debug('Switch %s has a password issue', self.switch_name)
                child.close()
                raise PasswordError('Switch has a password issue')
            if i==4:
                TIMEOUT=30
                if self.sys=='':
                    logging.debug("Switch is in loader prompt %s port %s",self.console_ip,self.act_port)
                    child.close()
                    raise LoaderError('load_image_using_telnet, switch in loader prompt')
                child.sendline('boot %s'%(self.sys))
            if (i>4 and i<8):
                TIMEOUT = 1200
            if i==8:
                TIMEOUT = 30
                child.sendline('yes')
            if (i>8 and i<12):
                TIMEOUT=30
                child.sendline('no')
            if i==12:
                TIMEOUT=30
                child.sendline(self.switch_pwd)
            if i==13:
                TIMEOUT=30
                child.sendline('admin')
            if i==14:
                TIMEOUT=30
                child.sendline(self.switch_pwd)
            if i>14 and i<17:
                TIMEOUT=5
                child.sendline('exit')
            if i==17:
                TIMEOUT=30
                child.sendline('')
            if i==18:
                logging.debug("Switch is in boot prompt %s port %s",self.console_ip,self.act_port)
                child.close()
                raise LoaderError('load_image_using_telnet, switch in loader prompt')
            if i==19:
                logging.info("**** (Loading image)/(Telnet to switch) is successful ****")
                break
            i = child.expect([pexpect.TIMEOUT, pexpect.EOF, r'Invalid admin', r'Wrong Password', 'loader>.*', \
                    'Booting kickstart image:', 'Checking all filesystems', 'INIT: Entering runlevel', \
                    'Abort Auto Provisioning and continue.*', 'enable admin vdc.*', 'enforce secure password.*', \
                    'the basic configuration dialog.*', 'the password for.*', SWITCH_LOGIN, PWD_PROMPT, \
                    BASH_SHELL, DEBUG_SHELL, 'wish to continue:', r'switch.boot.#',  SWITCH_PROMPT], timeout=TIMEOUT)
        
        child.sendline('')
        child.expect(SWITCH_PROMPT)
        return child

    def ascii_copy(self, switch_cons):
        """
        This method is to copy the running confing to run_power_config and
        startup config to start_power_config. Then save both the files to
        remote server.
        This will even store the kickstart/system image loaded to the same
        remote server which will be loaded while reloading the setup.
        """
        sys = ""
        founds = 0
        
        switch_cons.sendline('switchback')
        switch_cons.expect(SWITCH_PROMPT)

        #For storing the kickstart and the system images
        switch_cons.sendline('show version | grep "image file is"')
        switch_cons.expect(SWITCH_PROMPT)
        string = switch_cons.before
        if "///" in string:
            sys = string.split('///')[1]
            sys = sys.split()[0]
        if sys != "":
            switch_cons.sendline('dir')
            switch_cons.expect(SWITCH_PROMPT)
            dir = switch_cons.before
            imgs = dir.split()
            if sys in imgs:
                founds = 1

        logging.info("Found sys %d", founds)
        if founds==1:
            Utils.update_images(self.switch_name,"",sys)
        else:
            Utils.update_images(self.switch_name,"","")

        #Now write erase and copy the running config to file
        switch_cons.sendline('delete run_power_config n')
        switch_cons.expect(SWITCH_PROMPT, 60)
        switch_cons.sendline('delete start_power_config n')
        switch_cons.expect(SWITCH_PROMPT, 60)

        #no boot kick and sys
        switch_cons.sendline('config t')
        switch_cons.expect(SWITCH_PROMPT)
        switch_cons.sendline('no boot nxos')
        switch_cons.expect(SWITCH_PROMPT, 60)
        #write erase
        switch_cons.sendline('write erase')
        switch_cons.expect('Do you wish to proceed anyway')
        switch_cons.sendline('y')
        switch_cons.expect(SWITCH_PROMPT, 120)
        #write erase boot
        switch_cons.sendline('write erase boot')
        switch_cons.expect('Do you wish to proceed anyway')
        switch_cons.sendline('y')
        switch_cons.expect(SWITCH_PROMPT, 120)
        
        Switch.setip(switch_cons,self.mgmt_ip)
        #Copy the kickstart and system image to server only if present
        if founds==1:
            d_file = "%s/%s.system.gbin"%(self.switch_name,self.switch_name)
            Switch.copy_files_to_server(switch_cons=switch_cons,s_file=sys,d_file=d_file)

        "Now copy the running config to run_power_config file"
        switch_cons.sendline('show running-config vdc-all > run_power_config')
        i = switch_cons.expect([SWITCH_PROMPT,r'yes/no',pexpect.TIMEOUT, pexpect.EOF])
        if i==0:
            pass
        if i==1:
            switch_cons.sendline('yes')
            switch_cons.expect(SWITCH_PROMPT,180)
        if i==2 or i==3:
            logging.info("Something wrong with switch %s",self.switch_name)
            return False
        
        d_file = "%s/%s.run_power_config"%(self.switch_name,self.switch_name)
        Switch.copy_files_to_server(switch_cons=switch_cons,s_file='run_power_config',d_file=d_file)
        
        "Now copy the startup config to run_power_config file"
        switch_cons.sendline('show startup-config vdc-all > start_power_config')
        i = switch_cons.expect([SWITCH_PROMPT,r'yes/no',pexpect.TIMEOUT, pexpect.EOF])
        if i==0:
            pass
        if i==1:
            switch_cons.sendline('yes')
            switch_cons.expect(SWITCH_PROMPT,180)
        if i==2 or i==3:
            logging.info("Something wrong with switch %s",self.switch_name)
            return False
        
        d_file = "%s/%s.start_power_config"%(self.switch_name,self.switch_name)
        Switch.copy_files_to_server(switch_cons=switch_cons,s_file='start_power_config',d_file=d_file)
        
        return True

    def copy_images_to_switch(self):
        """
        This definition is to copy the right set of images to switch which
        has been used for sanities for other its not required so just return
        """
        dir = ''
        logging.info("Copy the sys=%s images if not available to the switch", self.sys)
        console = pexpect.spawn('telnet %s %s'%(self.console_ip,self.act_port))
        console.logfile = self.log
        time.sleep(2)
        console.sendline('')
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, SWITCH_LOGIN, SWITCH_PROMPT, 'loader>.*'], 120)
        if i==0 or i==1:
            logging.debug(str(console))
            console.close()
            return
        if i==2 or i==3:
            if i==2:
                console.sendline('admin')
                console.expect('assword:')
                console.sendline(self.switch_pwd)
                console.expect(SWITCH_PROMPT)
            console.sendline('switchback')
            console.expect(SWITCH_PROMPT)
            console.sendline('terminal length 0')
            console.expect(SWITCH_PROMPT)
            console.sendline('dir')
            console.expect(SWITCH_PROMPT)
            dirs = console.before
            if self.sys in dirs.split():
                logging.info("Found the System image in bootflash")
                console.close()
                return
            logging.info("Did not find System image in bootflash")
        if i==4:
            console.sendline('')
            console.expect('loader>.*')
            console.sendline('dir')
            console.expect('loader>.*')
            dirs = console.before
            if self.sys in dirs.split():
                logging.info("Found the System image in bootflash")
                console.close()
                return
            logging.info("Did not find System image in bootflash")
        
        if i==2 or i==3:
            console.sendline('reload')
            console.expect('y/n')
            console.sendline('y')
            console.expect('loader>.*', 60)
        
        console.sendline('')
        i = console.expect([pexpect.TIMEOUT, pexpect.EOF, 'loader>.*'])
        if i==0 or i==1:
            logging.debug(str(console))
            console.close()
            return
        if i==2:
            console.sendline('dir')
            console.expect('loader>.*')
            imgs = n9kSwitch.get_images_in_switch(console.before)
            for im in imgs:
                match = re.match(r'n9.*dk9([0-9A-Za-z\.]+)', im)
                if match:
                    break
            console.sendline('boot %s' % im)
            console.exit()
            console = self.load_or_telnet_image(log)

        Switch.setip(console,self.mgmt_ip)
        
        for img in imgs:
            console.sendline('delete bootflash:%s' % img)
            console.expect(SWITCH_PROMPT)
        
        time.sleep(10)
        d_file = self.sys
        s_file = "%s/%s.system.gbin"%(self.switch_name,self.switch_name)
        Switch.copy_files_to_switch(switch_cons=console, s_file=s_file, d_file=d_file)
        d_file = "power_config"
        s_file = "%s/%s.run_power_config"%(self.switch_name,self.switch_name)
        Switch.copy_files_to_switch(switch_cons=console, s_file=s_file, d_file=d_file)
        s_file = "%s/%s.start_power_config"%(self.switch_name,self.switch_name)
        Switch.copy_files_to_switch(switch_cons=console, s_file=s_file, d_file=d_file)
        
        console.close()
        return

    def get_switch_module_details(self):
        """
        This function will retrieve the "show module | xml" details into a
        xml format which inturn will be returned to the caller
        """
        logging.info("Logging into switch %s to collect details", self.switch_name)
        xml = {}
        output = None
        xml['mgmt_issue'] = False
        xml['telnet_issue'] = False
        xml['inv'] = ""
        xml['uptime'] = ""
        xml['idletime'] = ""

        try:
            output = self.get_switch_details_from_mgmt("ssh")
        except (TimeoutError, EofError):
            xml['mgmt_issue'] = True 
            #Always Clear the Consoles while working on the console
            self.clear_console()
            self.clear_screen()
            #Check which port is active one
            if self.stnd_port:
                cons_ip = [self.console_ip, self.stnd_console_ip]
                ports = [self.act_port, self.stnd_port]
                checkpo0 = self.check_standby(cons_ip[0], ports[0])
                checkpo1 = self.check_standby(cons_ip[1], ports[1])
                if not(checkpo0) and not(checkpo1):
                    self.stnd_console_ip, self.stnd_port = cons_ip[1],ports[1]
                    self.console_ip,self.act_port = cons_ip[0],ports[0]
                if checkpo0:
                    self.stnd_console_ip, self.stnd_port = cons_ip[0],ports[0]
                    self.console_ip,self.act_port = cons_ip[1],ports[1]
                if checkpo1:
                    self.stnd_console_ip, self.stnd_port = cons_ip[1],ports[1]
                    self.console_ip,self.act_port = cons_ip[0],ports[0]
                Utils.update_console_ip_and_ports(self.switch_name, self.console_ip, \
                                self.act_port, self.stnd_console_ip, self.stnd_port)
            try:
                output = self.get_switch_details_from_console()
            except BootingError:
                try:
                    console = self.load_image_using_telnet()
                    console.close()
                    output = self.get_switch_details_from_mgmt("ssh")
                except (TimeoutError, EofError):
                    xml['telnet_issue'] = True
                    raise TimeoutError('Could not telnet nor ssh')
            except (TimeoutError, EofError):
                xml['telnet_issue'] = True
                raise TimeoutError('Could not telnet nor ssh')
        xml['clock'],xml['idletime'],xml['inv'],xml['uptime'] = \
                collections.OrderedDict(sorted(output.items())).values()
        return xml
