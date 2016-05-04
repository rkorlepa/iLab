#!/home/ilab/python2.7.11/bin/python

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
from ilab.Database import *

class Utils(object):
    #Create a seperate folder on the remote host to copy switch files
    def create_data_folder(self, switch):
        logging.info("Creating the folder %s in the remote host", switch)
        subprocess.call('rm -rf %s/%s' % (DATA_DIR ,switch), shell=True)
        subprocess.call('mkdir -p %s/%s' % (DATA_DIR ,switch), shell=True)
        return

    def delete_logfile(self, File):
        if not(os.path.isfile(File)):
            return
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(File)
        crdt = datetime.strptime(time.ctime(atime), "%a %b %d %H:%M:%S %Y")
        tdelta = crdt
        tdelta += timedelta(days=7)
        if tdelta < datetime.now():
            os.system('rm -rf %s' % File)
        return

    def update_images(self, switch_name, kick="", sys=""):
        switch = Switches.get(Switches.switch_name==switch_name)
        switch.kickstart = kick
        switch.system = sys
        switch.save()
        return
