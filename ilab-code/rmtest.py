#!/ws/rkorlepa-sjc/python/bin/python

import os
import re
import logging
from subprocess import call, check_output
from prompt_toolkit import prompt

from Utils import swUtils

from libilab import *
from libilab.Exceptions import *
from libilab.Database import *
from libilab.Switch import Switch 
from libilab.n3567kSwitch import n3567kSwitch 
from libilab.n89kSwitch import n89kSwitch

if __name__ == "__main__":
    tempList = []
    for switch in Switches.select():
        del tempList[:]
        for detail in Switch_Details.select().where(Switch_Details.id==switch.id):
            if re.search("(?i)supervisor", detail.module_type) or \
                    re.search("(?i)ethernet", detail.module_type):
                tempList.append(detail.linecard)
        switch.linecards = str(','.join(tempList))
        switch.save()

