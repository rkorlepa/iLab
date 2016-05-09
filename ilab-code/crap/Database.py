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
import logging

from datetime import datetime,timedelta,date
from Mysql import Mysql

import definitions as defn
import utils as util

class Database(object):

    def __init__(self, host, username, pwd, database, table=''):
        self._table = table
        self._conn = Mysql(host, username, pwd, database)
    
    def insert(self, table, *args, **kwargs):
        return self._conn.insert(table, *args, **kwargs)

    def delete(self, table, where=None, *args):
        return self._conn.delete(table, where, *args)

    def select(self, table, where=None, *args, **kwargs):
        return self._conn.select(table, where, *args, **kwargs)

    def update_ports(self, sw_name, act, stand):
        logging.info("Updating ActivePort=%s and StandbyPort=%s for switch=%s", act, stand, sw_name)
        self._conn.update(self._table, 'switch_name=%s', sw_name, active_port=act, standby_port=stand)

    def update_power_status(self, sw_name, power):
        logging.info("Updating is_powered_on as %s for switch=%s", power, sw_name)
        self._conn.update(self._table, 'switch_name=%s', sw_name, is_powered_on=power)

    def update_images(self, sw_name, kick, sys):
        logging.info("Updating kickstart=%s and system=%s images for switch=%s", kick, sys, sw_name)
        self._conn.update(self._table, 'switch_name=%s', sw_name, kickstart=kick, system=sys)

    def update_start_end_time(self, sw_name, start, end):
        self._conn.update(self._table, 'switch_name=%s', sw_name, start_time=start, end_time=end)

    def increment_end_time(self, switch_dict):
        logging.info("Incrementing end time based on weekday/weekend for switch=%s", str(switch_dict['switch_name']))
        dt = util.get_next_end_time(switch_dict)
        sw_name = str(switch_dict['switch_name'])
        self._conn.update(self._table, 'switch_name=%s', sw_name, end_time=dt)

    def increment_start_time(self, switch_dict):
        logging.info("Incrementing start timei based on weekday/weekend for switch=%s", str(switch_dict['switch_name']))
        dt = util.get_next_start_time(switch_dict)
        sw_name = str(switch_dict['switch_name'])
        self._conn.update(self._table, 'switch_name=%s', sw_name, start_time=dt)

    def update_is_sanity_activated(self, sw_name, status):
        logging.info("Updating is_sanity_activated as %s for switch=%s", status, sw_name)
        self._conn.update(self._table, 'switch_name=%s', sw_name, is_sanity_activated=status)
