#!/home/ilab/python2.7.11/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2015  The iLab Development Team
#
#  version = 3.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import sys
import pymongo
import os
import time
import json
import re

from datetime import datetime, date, timedelta
from optparse import OptionParser
from pymongo import MongoClient
from multiprocessing import Process

import definitions as defn
import utils as util
import data_from_db as dbase
import ilabmail as email
import powerFunction as pFunc

def update_hold_testbed(db,switch,reserve):
    db.switches.update({'switch_name' : switch},
                       {"$set" : {'hold_testbed' : reserve}
                       }
                      )
    return

def update_start_end_time(db,switch,start,end):
    db.switches.update({'switch_name' : switch},
                       {"$set" : {'start_time' : start,
                                  'end_time' : end}
                       }
                      )
    return

def update_testbed(db, switch, updatedict):
    db.switches.update({'switch_name' : switch},
                       {"$set" : updatedict}
                      )
    return

def printDetails(sw):
    print "Switch_Name\t\t -- %s" % str(sw['switch_name'])
    print "Console_Ip\t\t -- %s (admin|%s)" % (str(sw['console_ip']),str(sw['switch_pwd']))
    print "Console_Ports\t\t -- %s, %s" % (str(sw['active_port']), str(sw['standby_port']))
    print "Mgmt_Ip\t\t\t -- %s" % str(sw['mgmt_ip'])
    print "Switch_type\t\t -- %s" % str(sw['switch_type'])
    print "Power_Console_detail\t -- %s" % (str(sw['power_console_detail']))
    print "Sanity_Activated\t -- %s" % str(sw['is_sanity'])
    print "Sanity_Type\t\t -- %s" % str(sw['sanity_type'])
    print "Hold_Testbed\t\t -- %s" % str(sw['hold_testbed'])
    if str(sw['weekday_time']) != "":
        weekday_time = str(sw['weekday_time']).split('-')
        start = datetime.strptime(weekday_time[0], "%H:%M")
        end = datetime.strptime(weekday_time[1], "%H:%M")
        pst = start.strftime("%H:%M%p")
        pen = end.strftime("%H:%M%p")
        print "Weekday_time\t\t -- %s - %s" % (pst,pen) 
    else:
        print "Weekday_time\t\t -- %s" % str(sw['weekday_time']) 
    if str(sw['weekend_time']) != "":
        weekend_time = str(sw['weekend_time']).split('-')
        start = datetime.strptime(weekend_time[0], "%H:%M")
        end = datetime.strptime(weekend_time[1], "%H:%M")
        pst = start.strftime("%H:%M%p")
        pen = end.strftime("%H:%M%p")
        print "Weekend_time\t\t -- %s - %s" % (pst,pen) 
    else:
        print "Weekend_time\t\t -- %s" % str(sw['weekend_time'])
    print "Kickstart Image\t\t -- %s" % str(sw['kickstart'])
    print "System Image\t\t -- %s" % str(sw['system'])
    if str(sw['is_powered_on']).lower() == 'on':
        print "Switch Status\t\t -- ON"
    else:
        print "Switch Status\t\t -- OFF (%d hrs)" % sw['inactive_time']
    print "----------------------------------------------"
    return

def getSwitchDetails(sw):
    msg =  "Switch Name ---> " + str(sw['switch_name']) + "\n"
    msg += "Console Ip ---> " + str(sw['console_ip']) + "\n" 
    msg += "Console Ports ---> " + str(sw['active_port']) + "," + str(sw['standby_port']) + "\n" 
    msg += "Mgmt Ip ---> " + str(sw['mgmt_ip']) + "\n"
    msg += "Switch Type ---> " + str(sw['switch_type']) + "\n"
    msg += "Power_Console_detail ---> " + str(sw['power_console_detail']) + "\n"
    msg += "Sanity Testbed ---> " + str(sw['is_sanity']) + "\n" 
    msg += "Sanity Type ---> " + str(sw['sanity_type']) + "\n" 
    msg += "Hold Testbed ---> " + str(sw['hold_testbed']) + "\n" 
    msg += "Weedkay Time ---> " + str(sw['weekday_time']) + "\n" 
    msg += "Weekend Time ---> " + str(sw['weekend_time']) + "\n" 
    msg += "User ---> " + str(sw['user'])
    return msg

def insertFunc(sw, detail, insertSws, switches):
    '''Function to create the switch list to be added'''
    sw = str(sw).strip()
    if switches.find_one({'switch_name' : sw}) != None:
        print "Switch %s already exists in db" % sw
    else:
        #Collect the console ports with active port at index 0
        ports = str(detail['console_ports'])
        console_port = ports.split(',')
        if len(console_port) == 1:
            console_port.append('')
        console_port[0] = console_port[0].strip()
        console_port[1] = console_port[1].strip()

        #Collect the start and end time from weekday/weekend based on date.
        weekday_time = []
        weekend_time = []
        if str(detail['weekday_time']) != "":
            weekday_time = str(detail['weekday_time']).split('-')
            try:
                start = datetime.strptime(weekday_time[0], "%H:%M")
                end = datetime.strptime(weekday_time[1], "%H:%M")
            except Exception, e:
                print "JSON file has issue in time format with Switch=%s - %s" % (sw, str(e))
                sys.exit(0)
            
        if  str(detail['weekend_time'])!= "":
            weekend_time = str(detail['weekend_time']).split('-')
            try:
                start = datetime.strptime(weekend_time[0], "%H:%M")
                end = datetime.strptime(weekend_time[1], "%H:%M")
            except Exception, e:
                print "JSON file has issue in time format with Switch=%s - %s" % (sw, str(e))
                sys.exit(0)

        now = datetime.now()
        start_end = util.get_start_end_time(weekday_time,weekend_time, now)

        match = re.match(r'[0-9\.]+:[0-9\,]+:[a-zA-Z]+:[a-zA-Z0-9]+', str(detail['power_console_detail']))
        if match is None:
            print "JSON file has issue in power console detail format"
            sys.exit(0)

        if str(detail['switch_type']) not in defn.types:
            print "Switch Type is not defined as expected only n7k, n9k, xbow, n6k are supported"
            sys.exit(0)

        #Build the switch collection for adding to db
        switch = {
            'switch_name'		    : str(sw),
            'console_ip'		    : str(detail['console_ip']).strip(),
            'active_port'		    : console_port[0],
            'standby_port'		    : console_port[1],
            'mgmt_ip'		        : str(detail['mgmt_ip']).strip(),
            'switch_pwd'            : str(detail['switch_pwd']),
            'kickstart'		        : '',
            'system'		        : '',
            'weekday_time'          : str(detail['weekday_time']).strip(),
            'weekend_time'          : str(detail['weekend_time']).strip(),
            'start_time'		    : start_end['start'],
            'end_time'		        : start_end['end'],
            'power_console_detail'	: str(detail['power_console_detail']).strip(),
            'is_powered_on' 	    : 'on',
            'is_sanity' 		    : str(detail['is_sanity_testbed']).strip(),
            'inactive_time' 		: 0.0,
            'delay_off'             : 0,
            'is_sanity_activated'	: 'no',
            'switch_type'           : str(detail['switch_type']),
            'sanity_sw_name'	    : str(detail['sanity_testbed_name']),
            'hold_testbed'		    : str(detail['hold_switch']).strip(),
            'sanity_type'           : str(detail['sanity_type']).strip(),
            'sanity_nodes'          : str(detail['sanity_nodes']).strip(),
            'sanity_node_names'     : str(detail['sanity_node_names']).strip(),
            'user'            : str(detail['user_mail'])
            }
        insertSws.append(switch)

def insertSwitch(file):
    insertSws = []
    with open(file) as f:
        try:
            sws = json.load(f)
        except Exception, e:
            print str(e)
            print "Issue in you JSON file please check and try again"
            sys.exit(1)
    
    db = dbase.connect_mongodb()
    switches = db.switches
    try:
        for sw,detail in sws.items():
            insertFunc(sw,detail,insertSws, switches)
        from_list = 'rkorlepa@cisco.com'
        to_list = ''
        mailer = email.ICEmail(from_list, to_list)
        for s in insertSws:
            sw_id = switches.insert_one(s).inserted_id
            print "Switch %s has been added to db....HURRAH....GO GREEN" % s['switch_name']
            to_list = str(s['user'])
            mailer.set_to(to_list)
            subject = 'Welcome to iLab'
            if s['end_time'] == "":
                body = '%s has been added to iLab Database and will be Powered OFF right away as time slots have not been provided' % (s['switch_name'])
            else:
                t = s['end_time'].strftime("%A %H:%M %p")
                body = '%s has been added to iLab Database and will be Powered OFF or Activated for Sanities on %s' % (s['switch_name'], t)
            mailer.add_line(body)
            blank = ''
            mailer.add_line(blank)
            msg = getSwitchDetails(s)
            mailer.add_line(msg)
            util.send_email(mailer=mailer, subject=subject)
            if s['start_time'] == "" and s['end_time'] == "":
                p = Process(target=pFunc.powerOff, args=(s, db))
                p.start()
    except Exception as e:
        print str(e)
        sys.exit(1)
    return

def updateSwitch(file):
    with open(file) as f:
        try:
            sws = json.load(f)
        except Exception, e:
            print str(e)
            print "Issue in you JSON file please check and try again"
            sys.exit(1)
    
    db = dbase.connect_mongodb()
    switches = db.switches
    updateSw = {}
    for sw,detail in sws.items():
        updateddict = {}
        #If the switch itself doesnt exit then just add it into db
        switch = switches.find_one({'switch_name' : sw})
        if switch == None:
            insertSw = []
            try:
                insertFunc(sw,detail,insertSw,switches)
                for s in insertSw:
                    sw_id = switches.insert_one(s).inserted_id
                    print "Switch %s has been added to db....HURRAH....GO GREEN" % s['switch_name']
            except Exception, e:
                print str(e)
            continue
        for key,value in detail.items():
            #The below section is to compute a dictionary of only those values
            #which have been chaned in the JSON from what has been entered in db
            value = str(value).strip()
            if key == 'console_ip':
                if str(switch['console_ip']) != value:
                    updateddict['console_ip'] = value
            if key == 'console_ports':
                ports = []
                ports.append(str(switch['active_port']))
                ports.append(str(switch['standby_port']))
                giports = value.split(',')
                if len(giports) == 1:
                    giports.append('')
                giports[0] = giports[0].strip()
                giports[1] = giports[1].strip()
                if ports != giports:
                    updateddict['active_port'] = giports[0]
                    updateddict['standby_port'] = giports[1]
            if key == 'mgmt_ip':
                if str(switch['mgmt_ip']) != value:
                    updateddict['mgmt_ip'] = value
            if key == 'power_console_detail':
                if str(switch['power_console_detail']) != value:
                    updateddict['power_console_detail'] = value
            if key == 'is_sanity_testbed':
                if str(switch['is_sanity']) != value:
                    updateddict['is_sanity'] = value
            if key == 'weekday_time':
                weekday_time = value.split('-')
                try:
                    start = datetime.strptime(weekday_time[0], "%H:%M")
                    end = datetime.strptime(weekday_time[1], "%H:%M")
                except Exception, e:
                    print str(e)
                    sys.exit(0)

                if str(switch['weekday_time']) != value:
                    updateddict['weekday_time'] = value
            if key == 'weekend_time':
                if value != "":
                    weekend_time = value.split('-')
                    try:
                        start = datetime.strptime(weekend_time[0], "%H:%M")
                        end = datetime.strptime(weekend_time[1], "%H:%M")
                    except Exception, e:
                        print str(e)
                        sys.exit(0)

                if str(switch['weekend_time']) != value:
                    updateddict['weekend_time'] = value
            if key == 'hold_switch':
                if str(switch['hold_testbed']) != value:
                    updateddict['hold_testbed'] = value
            if key == 'sanity_type':
                if str(switch['sanity_type']) != value:
                    updateddict['sanity_type'] = value
            if key == 'switch_pwd':
                if str(switch['switch_pwd']) != value:
                    updateddict['switch_pwd'] = value
            if key == 'sanity_testbed_name':
                if str(switch['sanity_sw_name']) != value:
                    updateddict['sanity_sw_name'] = value
            if key == 'sanity_nodes':
                if str(switch['sanity_nodes']) != value:
                    updateddict['sanity_nodes'] = value
            if key == 'sanity_node_names':
                if str(switch['sanity_node_names']) != value:
                    updateddict['sanity_node_names'] = value
        #Once computed the updateddict which has the changed key, value pairs
        #insert it into its respective switch dictionary and later update the db
        if len(updateddict) != 0:
            updateSw[sw] = updateddict

    for testbed, updict in updateSw.items():
        update_testbed(db, testbed, updict)
        print "Switch %s has been updated" % testbed
    return

def removeSwitch(switch):
    """Remove the switch details from the database"""
    db = dbase.connect_mongodb()
    switches = db.switches
    
    sw = switches.find_one({'switch_name': switch})
    if sw == None:
        print "Switch %s does not exist in Database" % switch
        return
    from_list = 'rkorlepa@cisco.com'
    to_list = str(sw['user'])
    mailer = email.ICEmail(from_list, to_list)
    subject = 'iLab - %s switch deleted from db' % switch
    body = "%s has been deleted from iLab database." % switch
    mailer.add_line(body)
    body = "Sorry if we have caused any inconvenience. We would be delighted to help resolve the issue and get the switch back in iLab."
    mailer.add_line(body)
    body = "Please feel free to contact/give feedback via the mailer iLab@cisco.com"
    mailer.add_line(body)
    body = ''
    mailer.add_line(body)
    body = "Wiki - http://wikicentral.cisco.com/display/PROJECT/iLab+-+Green+Lab"
    mailer.add_line(body)
    util.send_email(mailer=mailer, subject=subject)
    
    switches.remove({'switch_name' : switch})

    print "Switch %s has been removed from database" % switch
    return

def showSwitch(switch):
    """Show the all or specified switch details in the database"""
    db = dbase.connect_mongodb()
    switches = db.switches
    
    if switch == 'all': 
        for sw in switches.find():
            printDetails(sw)
    else:
        sw = switches.find_one({'switch_name' : switch})
        if sw:
            printDetails(sw)
        else:
            print "Switch %s does not exist in database" % switch
    return

def holdSwitch(switch):
    """Hold the switch i.e. do not donate it to lab or poweroff"""
    db = dbase.connect_mongodb()
    switches = db.switches
    
    if switches.find({'switch_name' : switch}).count() == 0:
        print "Switch %s does not exist in the database" % switch
        sys.exit(0)

    sw = switches.find_one({'switch_name' : switch})
    if str(sw['is_powered_on']).lower() == 'off':
        print "Switch %s cannot be held as its powered off/in sanities" % switch
        sys.exit(0)

    update_hold_testbed(db, switch=switch, reserve='yes')
    print "Switch %s has been held, will not be submitted for sanities or powered off until released" % switch
    return

def releaseSwitch(switch):
    """Release the switch i.e. donate it to lab or poweroff"""
    db = dbase.connect_mongodb()
    switches = db.switches

    if switches.find({'switch_name' : switch}).count() == 0:
		print "Switch %s does not exist in the database" % switch
		sys.exit(0)

    sw = switches.find_one({'switch_name': switch})
    weekday_time = []
    weekend_time = []
    weekday_time = str(sw['weekday_time']).split('-')
    weekend_time = str(sw['weekend_time']).split('-')
    now = datetime.now()
    start_end = util.get_start_end_time(weekday_time,weekend_time, now)

    update_hold_testbed(db, switch=switch, reserve='no')
    update_start_end_time(db, switch=switch, start=start_end['start'], end=start_end['end'])

    print "Switch %s has been released....HURRAH....GO GREEN" % switch
    return

def poweronSwitch(switch):
    """Power on the switch based on user explicity"""
    db = dbase.connect_mongodb()
    switches = db.switches
    sw = switches.find_one({'switch_name' : switch})
 
    print "Please sit back and relax will take around 10 min for the switch to come up...."
    print "(DO NOT CTRL+C)"
    pFunc.powerOn(sw,db,True)
    print "Switch %s is read for use" % switch
    return
