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
from Switch import Switch 
from Utils import Utils

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

    def ascii_copy(self, switch_cons):
        """
        This method is to 
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
        switch_cons.expect(SWITCH_PROMPT, 60)
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
        
        "Now copy the running config to run_power_config file"
        switch_cons.sendline('show running-config vdc-all > run_power_config')
        i = switch_cons.expect([SWITCH_PROMPT,r'yes/no',pexpect.TIMEOUT, pexpect.EOF])
        if i==0:
            pass
        if i==1:
            switch_cons.sendline('yes')
            switch_cons.expect(SWITCH_PROMPT,180)
        if i==2 or i==3:
            print "Something wrong with switch %s so go ahead and poweroff" % self.switch_name
            return False
        
        "Now copy the startup config to run_power_config file"
        switch_cons.sendline('show startup-config vdc-all > start_power_config')
        i = switch_cons.expect([SWITCH_PROMPT,r'yes/no',pexpect.TIMEOUT, pexpect.EOF])
        if i==0:
            pass
        if i==1:
            switch_cons.sendline('yes')
            switch_cons.expect(SWITCH_PROMPT,180)
        if i==2 or i==3:
            print "Something wrong with switch %s so go ahead and poweroff" % self.switch_name
            return False
        
        Switch.setip(switch_cons,self.mgmt_ip)

        #Copy the kickstart and system image to server only if present
        if founds==1:
            d_file = "%s/%s.system.gbin"%(self.switch_name,self.switch_name)
            Switch.copy_files_to_server(switch_cons=switch_cons,s_file=sys,d_file=d_file)
        d_file = "%s/%s.run_power_config"%(self.switch_name,self.switch_name)
        Switch.copy_files_to_server(switch_cons=switch_cons,s_file='run_power_config',d_file=d_file)
        d_file = "%s/%s.start_power_config"%(self.switch_name,self.switch_name)
        Switch.copy_files_to_server(switch_cons=switch_cons,s_file='start_power_config',d_file=d_file)
        
        return True

    def load_or_telnet_image(self, log):
        """
        This definition is to load the images from loader prompt
        Telnet handle is not closed in function needs to be handled by the caller
            loader> boot <system> (set password and get to loader prompt)
        If already at switch prompt just return the telnet handle
        """
        logging.info("Loading or Telnet to ip=%s with port=%s with sys=%s",self.console_ip,self.act_port,self.sys)
        TIMEOUT = 30
        child = pexpect.spawn('telnet %s %s'%(self.console_ip,self.act_port))
        child.logfile = log
        child.sendline('')
        time.sleep(3)
        i = child.expect([pexpect.TIMEOUT, pexpect.EOF, 'loader>.*', 'Booting kickstart image:', \
                'Checking all filesystems', 'INIT: Entering runlevel', 'Abort Auto Provisioning and continue.*', \
                'enable admin vdc.*', 'enforce secure password.*', 'the password for.*', \
                'the basic configuration dialog.*', SWITCH_LOGIN, 'Password:', BASH_SHELL, \
                DEBUG_SHELL, 'wish to continue:', r'switch.boot.#',  SWITCH_PROMPT], timeout=TIMEOUT)
        while i>=0:
            if i==0:
                TIMEOUT=30
                logging.debug('TIMEOUT exception. Here is what telnet said:')
                logging.debug(str(child))
                return False 
            if i==1:
                TIMEOUT=30
                logging.debug('TIMEOUT exception. Here is what telnet said:')
                logging.debug(str(child))
                return False
            if i==2:
                TIMEOUT=30
                if self.sys=='':
                    logging.debug("Switch is in loader prompt %s port %s",self.console_ip,self.act_port)
                    child.close()
                    return False
                child.sendline('boot %s'%(self.sys))
            if (i>2 and i<6):
                TIMEOUT = 1200
            if i==6:
                TIMEOUT = 30
                child.sendline('yes')
            if (i>6 and i<9):
                TIMEOUT=30
                child.sendline('no')
            if i==9:
                TIMEOUT=30
                child.sendline(self.switch_pwd)
            if i==10:
                TIMEOUT=30
                child.sendline('no')
            if i==11:
                TIMEOUT=30
                #print "admin"
                child.sendline('admin')
            if i==12:
                TIMEOUT=30
                #print "pwd"
                child.sendline(self.switch_pwd)
            if i>12 and i<15:
                TIMEOUT=5
                child.sendline('exit')
            if i==15:
                TIMEOUT=30
                child.sendline('')
            if i==16:
                logging.debug("Switch is in boot prompt %s port %s",self.console_ip,self.act_port)
                child.close()
                return False
            if i==17:
                logging.info("**** (Loading image)/(Telnet to switch) is successful ****")
                break
            #print "expect"
            i = child.expect([pexpect.TIMEOUT, pexpect.EOF, 'loader>.*', 'Booting kickstart image:', \
                    'Checking all filesystems', 'INIT: Entering runlevel', 'Abort Auto Provisioning and continue.*', \
                    'enable admin vdc.*', 'enforce secure password.*', 'the password for.*', \
                    'the basic configuration dialog.*', SWITCH_LOGIN, 'Password:', BASH_SHELL, \
                    DEBUG_SHELL, 'wish to continue:', r'switch.boot.#',  SWITCH_PROMPT], timeout=TIMEOUT)
        
        child.sendline('')
        child.expect(SWITCH_PROMPT)
        child.sendline('terminal length 0')
        child.expect(SWITCH_PROMPT)
        return child

    def copy_images_to_switch(self, log):
        """
        This definition is to copy the right set of images to switch which
        has been used for sanities for other its not required so just return
        """
        dir = ''
        logging.info("Copy the sys=%s images if not available to the switch", self.sys)
        console = pexpect.spawn('telnet %s %s'%(self.console_ip,self.act_port))
        console.logfile = log
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
