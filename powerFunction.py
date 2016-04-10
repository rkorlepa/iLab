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
from multiprocessing import Process
from datetime import datetime,timedelta,date

from n7kSwitch import n7kSwitch
from n9kSwitch import n9kSwitch
from Switch import Switch
from PowerConsole import Power

import utils as util
import definitions as defn
import ilabmail as email 

def powerOff(switch, db):
    #Set the logging file
    sw_name = str(switch['switch_name'])
    strfile = '%s%s.powerOff.log' % (defn.log_dir,sw_name)
    fout = file(strfile, 'a')
    logging.basicConfig(filename=strfile, format='%(asctime)s: %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    
    #Initialize the Switch details
    if str(switch['switch_type']).lower() == 'n9k':
        sw = n9kSwitch(switch)
    else:
        sw = n7kSwitch(switch)

    #Initialize the power console details
    power_detail = str(switch['power_console_detail'])
    power = Power(power_detail)
    
    #Delete the log file if its older than 1 week
    util.delete_logfile(strfile)

    logging.info("Start with powering off switch %s", sw.switch_name)
    #Check if its reserved for day
    if str(switch['hold_testbed']).lower() == 'yes':
        logging.info("Switch %s has been reserved for day so not powering off", sw.switch_name)
        db.increment_end_time(switch)
        #Send mail if testbed is in hold state.
        from_list = to_list = str(switch['user'])
        mailer = email.ICEmail(from_list, to_list)
        subject = "[iLab Hold Update] Testbed %s has been held" % sw.switch_name
        body = "Please release the testbed %s if its not used for extended testing" % sw.switch_name
        util.send_email(mailer=mailer, subject=subject, body=body)
        return
    #Check if its already powered off
    if str(switch['is_powered_on']).lower() == 'off':
        logging.info("No need to poweroff switch '%s', already off", sw.switch_name)
        return
    
    #Always Clear the Consoles while working on the script
    sw.clear_console(log=fout)
    sw.clear_screen(log=fout)

    #Check which port is active one
    if str(sw.stnd_port) != '':
        ports = [sw.act_port, sw.stnd_port]
        checkpo0 = sw.check_standby(port=ports[0],log=fout)
        checkpo1 = sw.check_standby(port=ports[1],log=fout)
        if not(checkpo0) and not(checkpo1):
            st_port = ports[1]
            port = ports[0]
        if checkpo0:
            st_port = ports[0]
            port = ports[1]
        if checkpo1:
            st_port = ports[1]
            port = ports[0]
        db.update_ports(sw.switch_name, port, st_port)
        sw.act_port = port
        sw.stnd_port = st_port
    
    logging.info("telnet ip %s and active port %s",sw.console_ip, sw.act_port)
    sw.clear_console(log=fout)
    
    #Time to copy the running-config to power_config file on switch 
    #and power off the box 
    util.folder_on_remote_host(switch=sw.switch_name, log=fout)
    switch_tel = sw.load_or_telnet_image(log=fout)
    db.update_power_status(str(switch['switch_name']), 'off')
    db.increment_end_time(switch)
    if isinstance(switch_tel,bool):
        logging.info("Since switch was in loader prompt there is nothing to save so just poweroff/donate")
        sw.kick = ""
        sw.sys = ""
        db.update_images(sw.switch_name, sw.kick, sw.sys)
    else:
        #Since everything looks good, now recreate the switch folder in the
        #remote host
        sw.ascii_copy(db, switch_tel)
        switch_tel.close()

    from_list = to_list = str(switch['user'])
    mailer = email.ICEmail(from_list, to_list)
    if str(switch['is_sanity']).lower() == 'yes':
        enable_sanity = 1
        #Only enable this sanity if its single node else check if other nodes 
        #are free to be activated
        if int(switch['sanity_nodes']) > 1:
            node_names = str(switch['sanity_node_names']).split(',')
            for node in node_names:
                if node != '':
                    other_sanity_switch =db.select("", "switch_name='"+str(node)+"'", "*")
                    if str(other_sanity_switch['is_powered_on']).lower() == 'on':
                        enable_sanity = 0
                        break

        if enable_sanity == 1:
            logging.info("Activate Sanity for testbed %s", sw.switch_name)
            util.activate_sanity_and_send_mail(db, switch, mailer)
        else:
            logging.info('Waiting for other testbeds %s', str(switch['sanity_node_names']))
            t = switch['start_time'].strftime("%A %H:%M %p")
            subject = "[iLab Update] Testbed %s has been allocated for sanities[Not Activated]" % (sw.switch_name)
            body = "Testbed %s will be activated once the other node %s is available for activation until %s" % (sw.switch_name, str(switch['sanity_node_names']), t)
            util.send_email(mailer=mailer, subject=subject, body=body)
    else:
        #power.power_console_on_off(whatToDo='off',log=fout)
        t = switch['start_time'].strftime("%A %H:%M %p")
        subject = "[iLab Update] %s switch has been powered off" % (sw.switch_name)
        body = "%s switch will be powered off until %s" % (sw.switch_name, t)
        util.send_email(mailer=mailer, subject=subject, body=body)

    fout.close()
    return

def powerOn(switch, db, cli_pon=False):
    #Set the logging file
    sw_name = str(switch['switch_name'])
    if cli_pon == False:
        strfile = '%s%s.powerOn.log' % (defn.log_dir,sw_name)
    else:
        strfile = '%s.powerOn.log' % (sw_name)
    fout = file(strfile, 'a')
    logging.basicConfig(filename=strfile, format='%(asctime)s: %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    
    #Initialize the Switch details
    if str(switch['switch_type']).lower() == 'n9k':
        sw = n9kSwitch(switch)
    else:
        sw = n7kSwitch(switch)

    #Initialize the power console details
    power_detail = str(switch['power_console_detail'])
    power = Power(power_detail)

    #Delete the log file if its older than 1 week
    util.delete_logfile(strfile)

    logging.info("Start with powering on switch %s", sw.switch_name)
    #Check if testbed is sanity activated, then do not power on
    if switch['is_sanity_activated'] == 'yes':
        logging.info("Switch %s cannot power on as the switch is sanity activated", sw.switch_name)
        print "Switch %s cannot power on as its sanity activated" % sw.switch_name
        return
    if str(switch['hold_testbed']).lower() == 'yes':
        logging.info("Switch %s has been reserved for day so not powering on", sw.switch_name)
        db.increment_start_time(switch)
        return
    #Check if its already powered on
    if str(switch['is_powered_on']).lower() == 'on':
        logging.info("No need to poweron switch '%s', already on", sw.switch_name)
        return
    
    #Now power on the switch
    power.power_console_on_off(whatToDo='on',log=fout)

    from_list = to_list = str(switch['user'])
    mailer = email.ICEmail(from_list, to_list)
    t = switch['end_time'].strftime("%A %H:%M %p")
    subject = "[iLab Update] %s has been powered on and ready for user use" % (sw.switch_name)
    body = "%s has been powered on and ready for use until %s" % (sw.switch_name, t)
    util.send_email(mailer=mailer, subject=subject, body=body)
    db.update_power_status(sw.switch_name, 'on')
    db.increment_start_time(switch)
    
    #Always Close the Consoles while working on the script
    sw.clear_console(log=fout)
    #Time to Load the switch with the image specified in the switchImages file
    #If its sanity testbed then bootflash will be erased so copy the images
    #to bootflash first only if the testbed was not in loader prompt during
    #power off or sanity activation
    if str(switch['is_sanity']).lower() == "yes":
        if sw.kick != "" and sw.sys != "":
            sw.copy_images_to_switch(log=fout)
    #Now reload the switch with previous user configs
    switch_tel = sw.load_or_telnet_image(log=fout)
    if isinstance(switch_tel,bool):
        logging.info("Since switch was in loader prompt there is nothing to load so just power on")
    else:
        Switch.setip(switch_tel,sw.mgmt_ip)
        switch_tel.close()
        #util.switch_details(db,sw,fout)
        sw.ascii_load(log=fout)

    fout.close()
    return
