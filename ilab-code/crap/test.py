#!/home/ilab/python2.7.11/bin/python

import logging
import pexpect
import re
#  version = 3.0

# this will be the method called by the pexpect object to log
def _write(*args, **kwargs):
    content = args[0]
    # let's ignore other params, pexpect only use one arg AFAIK
    if content in [' ', '', '\n', '\r', '\r\n']:
        return # don't log empty lines
    for eol in ['\r\n', '\r', '\n']:
        # remove ending EOL, the logger will add it anyway
        content = re.sub('\%s$' % eol, '', content)
    return logger.info(content) # call the logger info method with the reworked content


# our flush method
def _doNothing():
    pass

# get the logger
strfile = 'test.log' % (defn.log_dir,sw_name)
fout = file(strfile, 'a')
logging.basicConfig(filename=strfile)
logger = logging.getLogger()

# configure the logger
logger.handlers=[]
logger.addHandler(logging.StreamHandler())
logger.handlers[-1].setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.setLevel(logging.INFO)

# give the logger the methods required by pexpect
logger.write = _write
logger.flush = _doNothing

p = pexpect.spawn('echo "hello world !!"', logfile=logger)
p.expect('!!')
