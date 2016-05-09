#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import os, sys, time 
import traceback
import pexpect
import re
import logging
import telnetlib

from ilab import *

class BaseError(Exception):
    pass

class TimeoutError(BaseError):
    pass

class PasswordError(BaseError):
    pass

class EofError(BaseError):
    pass

class LoaderError(BaseError):
    pass

class InvalidCliError(BaseError):
    pass
