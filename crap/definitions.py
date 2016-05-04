#!/home/ilab/python2.7.11/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2015  The iLab Development Team
#
#  version = 3.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

'''Used for db connection and remote host switch files'''
HOST = '172.23.152.41'
HOST_PROMPT = '\~\$'

'''Used in loadimage definition'''
SWITCH_PROMPT = '#' 
SWITCH_LOGIN = 'login: '
BASH_SHELL = '\(shell\)>'
DEBUG_SHELL = 'Linux[a-zA-Z\(\)]*#'
SWITCH_STANDBY = '(standby)'

'''Used during power on/off of apc/pdu'''
POWER_PROMPT = '[#>]'
PX_POWER_PROMPT = 'clp:/->'
SSH_NEWKEY = '(?i)are you sure you want to continue connecting'

'''Used for clear console only'''
CONSOLE_PROMPT = '[a-zA-Z0-9_-]+>'
EN_CONSOLE_PROMPT = '[a-zA-Z0-9_-]+#'

'''Log directory in server'''
log_dir = '/home/ilab/iLab-logs/'
data_dir = '/home/ilab/iLab-switch-data/'

'''For JSON Check'''
types = ['n7k', 'xbow', 'n9k', 'n6k']

'''Used in get swtich details'''
sw_types = ['N77-F3','N7K-F3','N7K-F2']
