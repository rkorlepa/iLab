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

    def __init__(self, host, username, pwd, database):
        self._conn = Mysql(host, username, pwd, database)
    
    def insert(self, table, *args, **kwargs):
        return self._conn.insert(table, *args, **kwargs)

    def delete(self, table, where=None, *args):
        return self._conn.delete(table, where, *args)

    def select(self, table, where=None, *args, **kwargs):
        return self._conn.select(table, where, *args, **kwargs)

    def update(self, table, where=None, *args, **kwargs):
        return self._conn.update(table, where, *args, **kwargs)