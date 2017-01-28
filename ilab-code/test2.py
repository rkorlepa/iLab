#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os
import re
import logging
from subprocess import call, check_output
from prompt_toolkit import prompt

from libilab import *
from libilab.Database import *

from Utils import swUtils

if __name__ == "__main__":
    for switch in Switches.select().where(Switches.user=='praiyeng').dicts():
        switchId = str(switch['id'])
        swUtils.test.delay(switchId)
