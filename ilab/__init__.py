#!/ws/rkorlepa-sjc/python/bin/python

import sys, os,re 
import logging
from jinja2 import Environment, PackageLoader

'''Used for db connection and remote host switch files'''
DB_DATABASE = 'ilab_test'
DB_USER = 'ilab'
DB_PWD = 'nbv_12345'
DB_HOST = '172.23.152.145'
HOST_PROMPT = '\~\$'

'''Log directory in server'''
LOG_DIR = '/ws/rkorlepa-sjc/iLab-logs/'
DATA_DIR = '/home/ilab/iLab-switch-data/'

'''Used for clear console only'''
CONSOLE_PROMPT = '[a-zA-Z0-9_-]+>'
EN_CONSOLE_PROMPT = '[a-zA-Z0-9_-]+#'

'''Definitions to compare expect strings during telnet/ssh'''
SWITCH_PROMPT = '#' 
SWITCH_STANDBY = '(standby)'
SWITCH_LOGIN = '(?i)login:'
PWD_PROMPT = '(?i)password:'
BASH_SHELL = '\(shell\)>'
DEBUG_SHELL = 'Linux[a-zA-Z\(\)]*#'
INVALID_CLI = ['Invalid','invalid','command not found']
LOGIN_INCORRECT = '(?i)Login incorrect'
AUTH_ISSUE = '(?i)authentication failure'
LOADER_PROMPT = '(?i)loader>'
BOOT_PROMPT = '(?i)\(boot\)'

'''Definitions for power console of apc/pdu'''
POWER_PROMPT = '[#>]'
PX_POWER_PROMPT = 'clp:/->'
SSH_NEWKEY = '(?i)are you sure you want to continue connecting'


ilab_templates = Environment(loader=PackageLoader('ilab','templates'))

def ilab_template(name):
	return ilab_templates.get_template(name)
