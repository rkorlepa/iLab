#!/home/ilab/python2.7.11/bin/python

import sys
import pymongo
import os
import time
import json
import re

from datetime import datetime, date, timedelta
from pymongo import MongoClient

import definitions as defn
import utils as util
import data_from_db as dbase

def update_start_end_time(db,switch,start,end):
    db.switches.update({'switch_name' : switch},
                       {"$set" : {'start_time' : start,
                                  'end_time' : end}
                       }
                      )
    return

if __name__ == '__main__':
    """Release the switch i.e. donate it to lab or poweroff"""
    db = dbase.connect_mongodb()
    switches = db.switches

    for sw in switches.find():
        switch = str(sw['switch_name'])
        weekday_time = []
        weekend_time = []
        weekday_time = str(sw['weekday_time']).split('-')
        weekend_time = str(sw['weekend_time']).split('-')
        print switch, weekday_time, weekend_time

        now = datetime.now()
        start_end = util.get_start_end_time(weekday_time,weekend_time, now)

        update_start_end_time(db, switch=switch, start=start_end['start'], end=start_end['end'])
