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

from Mysql import Mysql

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
