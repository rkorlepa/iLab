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

from pymongo import MongoClient
from datetime import datetime,timedelta,date

import definitions as defn
import utils as util

def connect_mongodb():
    try:
        client = MongoClient(defn.HOST, defn.DB_PORT)
        client.server_info()
    except Exception, e:
        print "Database Connection Issue - %s" % str(e)
        sys.exit(1)

    db = client.powerproj
    return db

def update_port_entry(db,switch,active_port,standby_port):
	logging.info("Updating ActivePort=%s and StandbyPort=%s for switch=%s", active_port, standby_port, switch)
        kwargs = {"active_port":active_port,'standby_port':standby_port}
        db.update('', "switch_name='"+switch+"'", **kwargs)

def store_on_off_in_powerOutlets(db, switch, power):
    logging.info("Updating is_powered_on as %s for switch=%s", power, switch)
    kwargs = {"is_powered_on":power}
    db.update('', "switch_name='"+switch+"'", **kwargs)

def store_images_for_switch(db, switch, kick, sys):
	logging.info("Updating kickstart=%s and system=%s images for switch=%s", kick, sys, switch)
        kwargs = {"kickstart":kick,'system':sys}
        db.update('', "switch_name='"+switch+"'", **kwargs)

#This is the heart of the iLab tool. This will calculate the next poweroff time
#according to the user weekday and weekend time slots. There are various
#combinations which have been checked. So if any one changes any functionality
#needs to check these again.
# wd = "08:00-22:00", we = ""
# wd = "08:00-02:00", we = ""
# wd = "08:00-22:00", we = "08:00-22:00"
# wd = "08:00-02:00", we = "08:00-22:00"
# wd = "08:00-02:00", we = "08:00-02:00"
# wd = "08:00-22:00", we = "08:00-02:00"
# wd = "", we = "08:00-22:00"
# wd = "", we = "08:00-02:00"
# wd = "", we = ""
#Different cases of manipulation is done only when weekday or weekend start 
def get_next_end_time(switch):
    if str(switch['weekday_time']) == "" and str(switch['weekend_time']) == "":
        return ""

    now = sw_end_time = switch['end_time']
    next_day = sw_end_time + timedelta(days=1)
    prev_day = sw_end_time - timedelta(days=1)
    weekday_time = []
    weekend_time = []
    if (str(switch['weekday_time'])) != "":
        weekday_time = str(switch['weekday_time']).split('-')
        st_wd_h = weekday_time[0].split(':')
        en_wd_h = weekday_time[1].split(':')
        end_wd = datetime.strptime(weekday_time[1], "%H:%M")
    if (str(switch['weekend_time'])) != "":
        weekend_time = str(switch['weekend_time']).split('-')
        st_we_h = weekend_time[0].split(':')
        en_we_h = weekend_time[1].split(':')
        end_we = datetime.strptime(weekend_time[1], "%H:%M")

    if sw_end_time.isoweekday() == 5 or sw_end_time.isoweekday() == 6:
        if (str(switch['weekday_time'])) != "":
            if int(en_wd_h[0]) < int(st_wd_h[0]):
                if sw_end_time.isoweekday() == 5:
                    sw_end_time += timedelta(days=1)
                    return sw_end_time
                if sw_end_time.isoweekday() == 6:
                    if (str(switch['weekend_time'])) != "":
                        if int(en_we_h[0]) < int(st_we_h[0]):
                            sw_end_time = datetime(next_day.year, next_day.month, next_day.day, end_we.hour, end_we.minute)
                        else:
                            if end_we.hour != sw_end_time.hour:
                                sw_end_time = datetime(now.year, now.month, now.day, end_we.hour, end_we.minute)
                            else:
                                sw_end_time += timedelta(days=1)
                        return sw_end_time
                    else:
                        temp = datetime(now.year, now.month, now.day, end_wd.hour, end_wd.minute)
                        sw_end_time = temp + timedelta(days=-temp.weekday(), weeks=1)
                        if int(en_wd_h[0]) < int(st_wd_h[0]):
                            sw_end_time += timedelta(days=1)
                        return sw_end_time
        if sw_end_time.isoweekday() == 5:
            if (str(switch['weekend_time'])) != "":
                if int(en_we_h[0]) < int(st_we_h[0]):
                    sw_end_time = datetime(next_day.year, next_day.month, next_day.day, end_we.hour, end_we.minute)
                    sw_end_time += timedelta(days=1)
                else:
                    sw_end_time = datetime(next_day.year, next_day.month, next_day.day, end_we.hour, end_we.minute)
                return sw_end_time
            else:
                temp = datetime(now.year, now.month, now.day, end_wd.hour, end_wd.minute)
                sw_end_time = temp + timedelta(days=-temp.weekday(), weeks=1)
                if int(en_wd_h[0]) < int(st_wd_h[0]):
                    sw_end_time += timedelta(days=1)
                return sw_end_time

    if sw_end_time.isoweekday() == 7 or sw_end_time.isoweekday() == 1:
        if (str(switch['weekend_time'])) != "":
            if int(en_we_h[0]) < int(st_we_h[0]):
                if sw_end_time.isoweekday() == 7:
                    sw_end_time += timedelta(days=1)
                    print sw_end_time
                    return sw_end_time
                if sw_end_time.isoweekday() == 1:
                    if (str(switch['weekday_time'])) != "":
                        if int(en_wd_h[0]) < int(st_wd_h[0]):
                            sw_end_time = datetime(next_day.year, next_day.month, next_day.day, end_wd.hour, end_wd.minute)
                        else:
                            if end_wd.hour != sw_end_time.hour:
                                sw_end_time = datetime(now.year, now.month, now.day, end_wd.hour, end_wd.minute)
                            else:
                                sw_end_time += timedelta(days=1)
                        return sw_end_time
                    else:
                        temp = timedelta((12-sw_end_time.weekday()) % 7)
                        sw_end_time = sw_end_time + temp
                        if int(en_we_h[0]) < int(st_we_h[0]):
                            sw_end_time += timedelta(days=1)
                        return sw_end_time
        if sw_end_time.isoweekday() == 7:
            if (str(switch['weekday_time'])) != "":
                if int(en_wd_h[0]) < int(st_wd_h[0]):
                    sw_end_time = datetime(next_day.year, next_day.month, next_day.day, end_wd.hour, end_wd.minute)
                    sw_end_time += timedelta(days=1)
                else:
                    sw_end_time = datetime(next_day.year, next_day.month, next_day.day, end_wd.hour, end_wd.minute)
                return sw_end_time
            else:
                temp = timedelta((12-sw_end_time.weekday()) % 7)
                sw_end_time = sw_end_time + temp
                if int(en_we_h[0]) < int(st_we_h[0]):
                    sw_end_time += timedelta(days=1)
                return sw_end_time

    sw_end_time += timedelta(days=1)
    return sw_end_time

#This is the heart of iLab tool. This is very straightforward as the power on will
#always be done at the start and no overlap is done based on end time as is for
#get_next_end_time function above.
def get_next_start_time(switch):
    if str(switch['weekday_time']) == "" and str(switch['weekend_time']) == "":
        return ""

    now = sw_start_time = switch['start_time']
    next_day = sw_start_time + timedelta(days=1)
    prev_day = sw_start_time - timedelta(days=1)
    weekday_time = []
    weekend_time = []
    if (str(switch['weekday_time'])) != "":
        weekday_time = str(switch['weekday_time']).split('-')
        st_wd_h = weekday_time[0].split(':')
        en_wd_h = weekday_time[1].split(':')
        start_wd = datetime.strptime(weekday_time[0], "%H:%M")
    if (str(switch['weekend_time'])) != "":
        weekend_time = str(switch['weekend_time']).split('-')
        st_we_h = weekend_time[0].split(':')
        en_we_h = weekend_time[1].split(':')
        start_we = datetime.strptime(weekend_time[0], "%H:%M")

    if sw_start_time.isoweekday() == 5:
        if (str(switch['weekend_time'])) != "":
            sw_start_time = datetime(next_day.year, next_day.month, next_day.day, start_we.hour, start_we.minute)
        else:
            temp = datetime(now.year, now.month, now.day, start_wd.hour, start_wd.minute)
            sw_start_time = temp + timedelta(days=-temp.weekday(), weeks=1)
        return sw_start_time

    if sw_start_time.isoweekday() == 7:
        if (str(switch['weekday_time'])) != "":
            sw_start_time = datetime(next_day.year, next_day.month, next_day.day, start_wd.hour, start_wd.minute)
        else:
            temp = timedelta((12-sw_start_time.weekday()) % 7)
            sw_start_time = sw_start_time + temp
        return sw_start_time

    sw_start_time += timedelta(days=1)
    return sw_start_time

def increment_end_time(db, switch):
    logging.info("Incrementing end time based on weekday/weekend for switch=%s", str(switch['switch_name']))
    dt = get_next_end_time(switch)
    sw_name = str(switch['switch_name'])
    kwargs = {"end_time":str(dt)}
    db.update('', "switch_name='"+sw_name+"'", **kwargs)

def increment_start_time(db, switch):
    logging.info("Incrementing start timei based on weekday/weekend for switch=%s", str(switch['switch_name']))
    dt = get_next_start_time(switch)
    sw_name = str(switch['switch_name'])
    kwargs = {"start_time":str(dt)}
    db.update('', "switch_name='"+sw_name+"'", **kwargs)

def delay_poweroff(db, switch):
    logging.info("Delay power off of switch %s by 30 minutes", str(switch['switch_name']))
    sw_name = str(switch['switch_name'])
    delay = switch['delay_off'] + 1
    delay_min = 30*delay
    end_dt = switch['end_time'] + timedelta(minutes=delay_min)
    #suppose the delay exceeds the next start time then there is no use to 
    if switch['start_time'] <= end_dt:
        delay = 0
        increment_start_time(switch)
        increment_end_time(switch)
    kwargs = {"delay_off":str(delay)}
    db.update('', "switch_name='"+sw_name+"'", **kwargs)

def set_is_sanity_activated(db, switch):
	logging.info("Updating is_sanity_activated as yes for switch=%s", switch)
        kwargs = {"is_sanity_activated":"yes"}
        db.update('', "switch_name='"+switch+"'", **kwargs)

def unset_is_sanity_activated(db, switch):
	logging.info("Updating is_sanity_activated as no for switch=%s", switch)
        kwargs = {"is_sanity_activated":"no"}
        db.update('', "switch_name='"+switch+"'", **kwargs)

