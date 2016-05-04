#!/ws/rkorlepa-sjc/python/bin/python

import os, sys

'''Used for db connection and remote host switch files'''
DB_DATABASE = 'ilab'
DB_USER = 'ilab'
DB_PWD = 'nbv_12345'
DB_HOST = '172.23.152.145'
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
LOG_DIR = '/home/ilab/iLab-logs/'
DATA_DIR = '/home/ilab/iLab-switch-data/'

'''For JSON Check'''
types = ['n7k', 'xbow', 'n9k', 'n6k']
