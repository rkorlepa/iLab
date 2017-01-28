#!/ws/rkorlepa-sjc/python/bin/python

import tablib
from subprocess import call, check_output
from prompt_toolkit import prompt
from collections import defaultdict

from prettytable import PrettyTable

from libilab import *
from libilab.ilabmail import *
from libilab.Database import *

if __name__ == '__main__':
    hash_mang = defaultdict()
    #hash_sw = defaultdict()
    managers = ['jaipatel','irezhu','satnandi','mveerach', \
                'lthanvan','shbulusu','amitgup3','jsoosaim', \
                'kpatel','sigundet','sapna','vtalagad','spitta', \
                'bhalappa','nmeiyyap','nasharma','srduvvur', \
                'akagarg','pkatti','rshank','masaxena','asuvacki', \
                'skailas','hahamed','pdharmam','shahnaz','nelsonm', \
                'sathenag','sraja','msyadav','mbandi','maheshc']
    for mang in managers:
        hash_mang[mang] = 0
    
    #for switch in Switches.select().where(Switches.director=='maheshc').dicts():
    #    hash_sw[str(switch['switch_name'])] = str(switch['user'])

    for mang in managers:
        users = check_output(['/usr/cisco/bin/rchain','-R','-h \
                %s' % mang]).split()
        for user in users:
            hash_mang[mang] = hash_mang[mang] + \
                    Switches.select().where(Switches.user==user.lower()).count()
            #for switch in Switches.select().where(Switches.user==user.lower()).dicts():
            #    if str(switch['switch_name']) in hash_sw.keys():
            #        del hash_sw[str(switch['switch_name'])]

    table = PrettyTable(["Manager","# of switches"])
    table.align["Mangers"] = "1"
    table.padding_width = 1
    for key, value in hash_mang.items():
        table.add_row([key, value])

    print table
