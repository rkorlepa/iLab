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

from datetime import datetime,timedelta,date

import data_from_db as dbase
import utils as util
import ilabmail as email 

def reset_inactive_time(db):
    kwargs = {'inactive_time':0.0}
    db.update('', '', **kwargs)
    return

if __name__ == '__main__':
    db = dbase.connect_mongodb()
    switches = db.switches
    total_off_time = 0.0
    total_sanity_time = 0.0 
    num_off = 0
    num_sanity = 0
    for switch in switches.find({'is_sanity':'no'}):
        num_off = num_off + 1
        total_off_time += switch['inactive_time'] 

    for switch in switches.find({'is_sanity':'yes'}):
        num_sanity = num_sanity + 1
        total_sanity_time += switch['inactive_time'] 
    
    from_list = 'rkorlepa@cisco.com'
    to_list = 'jaipatel@cisco.com'
    mailer = email.ICEmail(from_list, to_list)
    
    subject = '[iLab] Nexus7000: Green Lab Time Analysis'
    mailer.set_subject(subject)

    body = 'Number of switches in Green Lab are %d with total powered off time as of today is %.2f hours' \
            % (num_off, total_off_time)
    mailer.add_line(body)
    body = 'Number of switches for Sanities are %d with total sanity time as of today is %.2f hours' \
            % (num_sanity, total_sanity_time)
    mailer.add_line(body)
    mailer.send()
    mailer.reset()
    reset_inactive_time(db)
