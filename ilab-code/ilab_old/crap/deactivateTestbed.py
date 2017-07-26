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
import subprocess

from datetime import datetime, date, timedelta

import data_from_db as dbase
import utils as util
import ilabmail as email

if __name__=='__main__':
    db = dbase.connect_mongodb()
    sanities = db.sanities
    switches = db.switches
    for sanity in sanities.find():
        sanType = str(sanity['sanity_type']).lower()
        endTime = datetime.now()
        endTime += timedelta(minutes=int(sanity['time']))
        for switch in switches.find({'is_powered_on':'off', \
                                     'is_sanity_activated': 'yes', \
                                     'sanity_type': sanType, \
                                     'start_time': {'$lt': endTime}}):
            sw_name = str(switch['switch_name'])
            from_list = to_list = str(switch['user'])
            mailer = email.ICEmail(from_list, to_list)
            util.deactivate_sanity_and_send_mail(db, switch, mailer)
            dbase.unset_is_sanity_activated(db,sw_name)
