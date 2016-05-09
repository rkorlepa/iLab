#!/home/ilab/python2.7.11/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2015  The iLab Development Team
#
#  version = 3.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os,sys,time
import traceback
import re
import logging

from datetime import datetime,timedelta,date

import data_from_db as dbase

def update_inactive_time(db, switch, inactive_time):
    db.switches.update({'switch_name' : switch},
                       {"$set" : {'inactive_time' : inactive_time}}
                      )
    return

if __name__ == '__main__':
    db = dbase.connect_mongodb()
    switches = db.switches
    now = datetime.now()
    now_future = now + timedelta(hours=1)
    now_past = now - timedelta(hours=1)
    for switch in switches.find({'is_powered_on':'off'}):
        inactive_time = switch['inactive_time']
        sw_start_time = switch['start_time']
        sw_end_time = switch['end_time']
        if str(sw_start_time) == "" or str(sw_end_time) == "":
            inactive_time = inactive_time +1
        elif now_past < sw_end_time:
            mins = ((60-sw_end_time.minute)*1.0)/60
            inactive_time = inactive_time + mins
        elif now_future > sw_start_time:
            mins = (sw_start_time.minute*1.0)/60
            inactive_time = inactive_time + mins
        else:
            inactive_time = inactive_time + 1
        update_inactive_time(db=db, switch=str(switch['switch_name']), inactive_time=inactive_time)
