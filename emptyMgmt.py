#!/ws/rkorlepa-sjc/python/bin/python

from Database import *
from subprocess import check_output
import ilabmail as email
from collections import defaultdict

def send_email(switch_name, user, uid):
    from_list = to_list = uid + "@cisco.com"
    mailer = email.ICEmail(from_list, to_list)
    subject = "iLab[ISSUE] Update Mgmt_ip"
    line = "Hello " + user + ","
    mailer.add_line(line)
    line = ''
    mailer.add_line(line)
    line = 'Thank you for updating iLab with your switch details. We are now running database consistency checks to ensure every switch detail is CORRECT and every switch is reachable via iLab'
    mailer.add_line(line)
    line = ''
    mailer.add_line(line)
    line = "We ran into an issue and need your help to rectify the iLab database entry in next 48 hours."
    mailer.add_line(line)
    line = ''
    mailer.add_line(line)
    line = 'PROBLEM ::'
    mailer.add_line(line)
    line = ''
    mailer.add_line(line)
    line = 'Switch Mgmt_ip is not entered in iLab for the switch names - %s' % switch_name
    mailer.add_line(line)
    line = ''
    mailer.add_line(line)
    line = 'SOLUTION ::'
    mailer.add_line(line)
    line = ''
    mailer.add_line(line)
    line = "Steps to fix the problem:"
    mailer.add_line(line)
    line = "1.\tOpen http://ilab.cisco.com/"
    mailer.add_line(line)
    line = "2.\tFill in the <switch_name> in the search field"
    mailer.add_line(line)
    line = "3.\tCheck the box and click on 'Edit'"
    mailer.add_line(line)
    line = "4.\tUpdate the mgmt_ip with the default vdc mgmt_ip. If your switch is behind a private network and needs to be accessed through a server then please add the right details of the server in Proxy Server IP field"
    mailer.add_line(line)
    line = "  \tEg:\t10.10.10.10:admin:password"
    mailer.add_line(line)
    line = "  \t   \tjohnxy:admin:password"
    mailer.add_line(line)
    line = ''
    mailer.add_line(line)
    line = 'For any queries please contact - ilab@cisco.com'
    mailer.add_line(line)
    mailer.set_subject(subject)
    mailer.send()
    mailer.reset()

if __name__ == '__main__':
    sendDict = defaultdict(list)
    for sw in Switches.select().where(Switches.mgmt_ip==''):
        users = str(sw.user).lower().split(',')
        for user in users:
            sendDict[sw.user].append(sw.switch_name)

    for key,val in sendDict.items():
        res = check_output(["/usr/cisco/bin/rchain","-h","-n %s" % (str(key))]).rstrip().split('\n')
        if res:
            name = ' '.join(res[-1].split()[1:])
            switches = str(', '.join(val))
            send_email(switches, name, str(key))
