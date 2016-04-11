#!/home/ilab/python2.7.11/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2015  The iLab Development Team
#
#
#  version = 3.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os, sys, time
import subprocess
import traceback
import pexpect
import re
import logging
import subprocess

from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup

import definitions as defn
import ilabmail as email 

def send_email(mailer, subject, body=''):
    mailer.set_subject(subject)
    if body != '':
        mailer.add_line(body)
    #mailer.send()
    mailer.reset()
    return

#Create a seperate folder on the remote host to copy switch files
def folder_on_remote_host(switch, log, pwd="nbv_1234"):
    logging.info("Creating the folder %s in the remote host", switch)
    subprocess.call('rm -rf %s/%s' % (defn.data_dir ,switch), shell=True)
    subprocess.call('mkdir -p %s/%s' % (defn.data_dir ,switch), shell=True)
    return

def delete_logfile(file):
    if not(os.path.isfile(file)):
        return
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file)
    crdt = datetime.strptime(time.ctime(atime), "%a %b %d %H:%M:%S %Y")
    tdelta = crdt
    tdelta += timedelta(days=7)
    if tdelta < datetime.now():
        os.system('rm -rf %s' % file)
    return

def get_start_end_time(switch):
    #Set start and end usage of switch/testbed according to weekday and weekend
    st_end_time = {}
    weekday_time = []
    weekend_time = []
    now = datetime.now()

    if str(switch['weekday_time']) != "":
        weekday_time = str(switch['weekday_time']).split('-')
        try:
            start = datetime.strptime(weekday_time[0], "%H:%M")
            end = datetime.strptime(weekday_time[1], "%H:%M")
        except Exception, e:
            print "JSON file has issue in time format with Switch=%s - %s" % (sw, str(e))
            sys.exit(0)
        
    if  str(switch['weekend_time'])!= "":
        weekend_time = str(switch['weekend_time']).split('-')
        try:
            start = datetime.strptime(weekend_time[0], "%H:%M")
            end = datetime.strptime(weekend_time[1], "%H:%M")
        except Exception, e:
            print "JSON file has issue in time format with Switch=%s - %s" % (sw, str(e))
            sys.exit(0)

    if len(weekday_time) != 2 and len(weekend_time) != 2:
        st_end_time['start'] = ""
        st_end_time['end'] = ""
        return st_end_time

    if now.isoweekday() in range(1,6):
        if len(weekday_time) == 2:
            start = datetime.strptime(weekday_time[0], "%H:%M")
            end = datetime.strptime(weekday_time[1], "%H:%M")
        else:
            start = datetime.strptime(weekend_time[0], "%H:%M")
            end = datetime.strptime(weekend_time[1], "%H:%M")

        try:
            if len(weekday_time) == 2:
                st_end_time['start'] = datetime(now.year, now.month, now.day, start.hour, start.minute)    
                st_end_time['end'] = datetime(now.year, now.month, now.day, end.hour, end.minute)
                #This is done if end time is greater than 00:00
                if st_end_time['start'].hour > st_end_time['end'].hour:
                    st_end_time['end'] += timedelta(days=1)
                st_end_time['start'] += timedelta(days=1)
            else:
                temp = timedelta((12-now.weekday()) % 7)
                temp = now + temp
                st_end_time['start'] = datetime(temp.year, temp.month, temp.day, start.hour, start.minute)
                st_end_time['end'] = datetime(temp.year, temp.month, temp.day, end.hour, end.minute)
                if st_end_time['start'].hour > st_end_time['end'].hour:
                    st_end_time['end'] += timedelta(days=1)
        except Exception, e:
            print str(e)
            sys.exit(0)
    else:
        if len(weekend_time) == 2:
            start = datetime.strptime(weekend_time[0], "%H:%M")
            end = datetime.strptime(weekend_time[1], "%H:%M")

            try:
                st_end_time['start'] = datetime(now.year, now.month, now.day, start.hour, start.minute)    
                st_end_time['end'] = datetime(now.year, now.month, now.day, end.hour, end.minute)
                #This is done if end time is greater than 00:00
                if st_end_time['start'].hour > st_end_time['end'].hour:
                    st_end_time['end'] += timedelta(days=1)
                st_end_time['start'] += timedelta(days=1)
            except Exception, e:
                print str(e)
                sys.exit(0)
        else:
            start = datetime.strptime(weekday_time[0], "%H:%M")
            end = datetime.strptime(weekday_time[1], "%H:%M")

            try:
                temp = datetime(now.year, now.month, now.day, start.hour, start.minute)
                st_end_time['start'] = temp + timedelta(days=-temp.weekday(), weeks=1)
                st_end_time['end'] = datetime(now.year, now.month, now.day, end.hour, end.minute)
                st_end_time['end'] -= timedelta(days=1)
            except Exception, e:
                print str(e)
                sys.exit(0)
    
    return st_end_time

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

def activate_sanity_and_send_mail(db, switch, mailer):
    #Now activate the switch/testbed
    sw_name = str(switch['switch_name'])
    db.update_is_sanity_activated(sw_name, 'yes')
    t = switch['start_time'].strftime("%A %H:%M")
    subject = "[iLab Sanity Update] Testbed %s has been activated for sanities" % (sw_name)
    body = "Testbed %s has been activated for sanities with sanity testbed name as %s until %s" % (sw_name, str(switch['sanity_sw_name']), t)
    send_email(mailer=mailer, subject=subject, body=body)
    node_names = str(switch['sanity_node_names']).split(',')
    for node in node_names:
        if node != '':
            other_sanity_switch = db.select("", "switch_name='"+str(node)+"'", "*")
            other_sw_name = str(other_sanity_switch['switch_name'])
            db.update_is_sanity_activated(other_sw_name, 'yes')
            t = other_sanity_switch['start_time'].strftime("%A %H:%M")
            subject = "[iLab Sanity Update] Testbed %s has been activated for sanities" % (other_sw_name)
            body = "Testbed %s has been activated for sanities with sanity testbed name as %s until %s" % (other_sw_name, str(switch['sanity_sw_name']), t)
            send_email(mailer=mailer, subject=subject, body=body)
    #Now activate them for sanities
    cli_cmd = '/usr/cisco/bin/earms testbedInfo %s -a -u mchhajer -reason DE_Testbed_Activate' % str(switch['sanity_sw_name']) 
    subprocess.call(cli_cmd, shell=True)
    return

def deactivate_sanity_and_send_mail(db, switch, mailer):
    #Now deactivate the switch/testbed
    sw_name = str(switch['switch_name'])
    cli_cmd = '/usr/cisco/bin/earms testbedInfo %s -d -u mchhajer -reason test_issu' % str(switch['sanity_sw_name']) 
    subprocess.call(cli_cmd, shell=True)
    db.update_is_sanity_activated(sw_name, 'no')
    t = switch['end_time'].strftime("%A %H:%M")
    subject = "[iLab Sanity Update] %s has been de-activated from sanities" % (sw_name)
    body = "%s has been de-activated from sanities with sanity testbed name as %s until %s" % (sw_name, str(switch['sanity_sw_name']), t)
    send_email(mailer=mailer, subject=subject, body=body)
    node_names = str(switch['sanity_node_names']).split(',')
    for node in node_names:
        if node != '':
            other_sanity_switch = db.select("", "switch_name='"+str(node)+"'", "*")
            other_sw_name = str(other_sanity_switch['switch_name'])
            db.update_is_sanity_activated(other_sw_name)
            t = other_sanity_switch['end_time'].strftime("%A %H:%M")
            subject = "[iLab Sanity Update] Testbed %s has been de-activated from sanities" % (other_sw_name)
            body = "Testbed %s has been de-activated from sanities with sanity testbed name as %s until %s" % (other_sw_name, str(switch['sanity_sw_name']), t)
            send_email(mailer=mailer, subject=subject, body=body)
    return

def remove_first_last_lines(string):
    ind1 = string.find('\n')
    ind2 = string.rfind('\n')
    return string[ind1+1:ind2]

def switch_details(db, sw_obj, man, fout):
    out = remove_first_last_lines(sw_obj.get_switch_module_details(fout))
    if out == "":
        return
    out = out.replace(" ","")
    out = out.replace("__readonly__", "readonly")
    xml_soup = BeautifulSoup(out, "html.parser")

    switchDetails = {}
    regexp = re.compile(r'fabric|system')
    switchDetails['switch_name'] = sw_obj.switch_name
    switchDetails['linecard'] = []
    switchDetails['module_type'] = []
    switchDetails['serial_num'] = []
    for modules in xml_soup.findAll('row_inv'):
        if regexp.search(str(modules.desc.text).lower()) is not None:
            pass
        else:
            switchDetails['linecard'].append(str(modules.productid.text))
            switchDetails['module_type'].append(str(modules.desc.text))
            switchDetails['serial_num'].append(str(modules.serialnum.text))

    if len(switchDetails['linecard']) != 0:
        db.delete(TABLE, 'switch_name=%s', sw_obj.switch_name)

    detail = {}
    print "Detail added for %s" % sw_obj.switch_name
    for i in range(0,len(switchDetails['linecard'])):
        detail['switch_name'] = sw_obj.switch_name
        detail['linecard'] = switchDetails['linecard'][i]
        detail['module_type'] = switchDetails['module_type'][i]
        detail['serial_num'] = switchDetails['serial_num'][i]
        detail['manager'] = man
        db.insert(TABLE, **detail)
        detail = {}
