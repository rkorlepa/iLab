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
from subprocess import call
from abc import ABCMeta, abstractmethod
from passlib.hash import sha256_crypt

from ilab import *
from ilab.Database import *

class Utils(object):
    @staticmethod
    def remove_known_hosts(ip):
        logging.info("Removing known_host entry for ip %s", ip)
        cli_cmd = 'sed -e "/%s/d" ~/.ssh/known_hosts > ~/.ssh/known_hosts.bk && /bin/mv ~/.ssh/known_hosts.bk ~/.ssh/known_hosts' % ip
        call(cli_cmd, shell=True)
        return

    @staticmethod
    def create_data_folder(switch):
        logging.info("Creating the folder %s in the remote host", switch)
        subprocess.call('rm -rf %s/%s' % (DATA_DIR ,switch), shell=True)
        subprocess.call('mkdir -p %s/%s' % (DATA_DIR ,switch), shell=True)
        return

    @staticmethod
    def delete_logfile(File):
        if not(os.path.isfile(File)):
            return
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(File)
        crdt = datetime.strptime(time.ctime(atime), "%a %b %d %H:%M:%S %Y")
        tdelta = crdt
        tdelta += timedelta(days=7)
        if tdelta < datetime.now():
            os.system('rm -rf %s' % File)
        return

    @staticmethod
    def update_images(switch_name, kick="", sys=""):
        switch = Switches.get(Switches.switch_name==switch_name)
        switch.kickstart = kick
        switch.system = sys
        switch.save()
        return

    @staticmethod
    def update_console_ip_and_ports(switch_name, c_ip="", act="", st_c_ip="", stnd=""):
        switch = Switches.get(Switches.switch_name==switch_name)
        switch.console_ip = c_ip
        switch.active_port = act
        switch.stnd_console_ip = st_c_ip
        switch.standby_port = stnd 
        switch.save()
        return

    @staticmethod
    def check_user(user, pwd):
        try:
            user_pwd = Login.get(Login.username==user).password
            return sha256_crypt.verify(pwd, user_pwd)
        except:
            return False
