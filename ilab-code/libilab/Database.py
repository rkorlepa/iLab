#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

from libilab import *
from peewee import *

db = MySQLDatabase(DB_DATABASE, user=DB_USER, passwd=DB_PWD, host=DB_HOST, threadlocals=True)

class MySQLModel(Model):
    class Meta:
        database = db

class Switches(MySQLModel):
    switch_name = CharField()
    sshconsole = CharField(null=True)
    mgmt_ip = CharField(null=True)
    console_ip = CharField()
    active_port = CharField()
    stnd_console_ip = CharField(null=True)
    standby_port = CharField(null=True)
    console_login = CharField(null=True)
    switch_pwd = CharField()
    power_console_detail = CharField(null=True)
    switch_type = CharField()
    weekday_time = CharField(null=True)
    weekend_time = CharField(null=True)
    hold_testbed = CharField()
    user = CharField()
    manager = CharField(null=True)
    project = CharField(null=True)
    location = CharField()
    sanity_sw_name = CharField(null=True)
    sanity_nodes = CharField(null=True)
    sanity_node_names = CharField(null=True)
    start_time = DateTimeField(null=True)
    end_time = DateTimeField(null=True)
    kickstart = CharField(null=True)
    system = CharField(null=True)
    is_powered_on = CharField(null=True)
    is_sanity = CharField(null=True)
    is_sanity_activated = CharField(null=True)
    linecards = CharField(null=True)
    comments = CharField(null=True)
    director = CharField(null=True)
    user_role = CharField(null=True)

class Switch_Details(MySQLModel):
    id = IntegerField()
    switch_name = CharField()
    linecard = CharField(null=True)
    serial_num = CharField(null=True)
    module_type = CharField(null=True)

class Switch_Status(MySQLModel):
    id = IntegerField()
    switch_name = CharField()
    telnet_issue = BooleanField(null=True)
    mgmt_issue = BooleanField(null=True)
    loader_prompt = BooleanField(null=True)
    password_issue = BooleanField(null=True)
    invalidcli_issue = BooleanField(null=True)
    sys_uptime = DateTimeField(null=True)
    idle_time = CharField(null=True)

class Login(MySQLModel):
    id = IntegerField()
    username = CharField()
    password = CharField()

class Linecards(MySQLModel):
    linecard = CharField()
    cost = IntegerField()

class sjc06_104(MySQLModel):
    model = CharField()
    serial_num = CharField()
    lab = CharField()
    aisle = CharField()
    location = CharField()
    user = CharField()

db.connect()
db.create_tables([Switches,Switch_Details,Switch_Status, Login, Linecards, sjc06_104], safe=True)
