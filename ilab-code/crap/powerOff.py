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
import powerFunction as pFunc
import utils as util

from multiprocessing import Process
from datetime import datetime,timedelta,date
from Database import Database

processes = []

if __name__ == "__main__":
    try:
        db = Database('127.0.0.1', 'root', '', 'ilab')
        # Reset the start and end time for the switches before powering off
        switches = []
        switches = db.select('', "end_time is NULL or end_time<='"+str(datetime.now())+"'", '*')
        for switch in switches:
            start_end = util.get_start_end_time(switch)
            db.update_start_end_time(switch['switch_name'], start_end['start'], start_end['end'])
        
        switches = []
        switches = db.select('', "end_time<='"+str(datetime.now())+"'", '*')
        for switch in switches:
            print switch['switch_name']
            p = Process(target=pFunc.powerOff, args=(switch, db))
            p.start()
            processes.append(p)
        for pr in processes:
            pr.join()
    except Exception, e:
        print str(e)
        traceback.print_exc()
        os._exit(1)
