#!/ws/rkorlepa-sjc/python/bin/python

#-----------------------------------------------------------------------------
#  Copyright (C) 2016  The iLab Development Team
#
#  version = 1.0
#  Distributed under the terms of the Cisco Systems Inc. The full license is
#  in the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import subprocess
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename

class IlabEmail:
    def __init__(self, from_list, to_list, cc_list='', bcc_list='rkorlepa@cisco.com'):
        self.from_list = from_list
        self.to_list = to_list
        self.cc_list = cc_list
        self.bcc_list = bcc_list
        self.subject = ''
        self.lines = []
        self.attachment = None 
        self.hostname = socket.gethostname()

    def set_from(self, from_list):
        self.from_list = from_list

    def set_to(self, to_list):
        self.to_list = to_list

    def set_subject(self, subject):
        self.subject = subject 
   
    def set_body_lines(self, lines):
        self.lines = lines

    def append_lines(self, lines):
        self.lines += lines

    def add_line(self, line):
        self.lines.append(line)

    def set_cc(self, cc_list):
        self.cc_list = cc_list

    def set_bcc(self, bcc_list):
        self.bcc_list = bcc_list
    
    def set_attachment(self, attachment):
        self.attachment = attachment

    def reset(self):
        self.subject = ''
        self.lines = []
        
    def send(self, send_to=''):
        'Send email with subject body and attachments'
        self.add_line('\nFrom Host = %s\n' % (self.hostname))
        body = MIMEText('\n'.join(self.lines),'html')
        msg = MIMEMultipart('alternative')
        msg['To'] = self.to_list
        if send_to:
            msg['To'] = send_to
        msg['From'] = self.from_list
        msg['Bcc'] = self.bcc_list
        msg['Cc'] = self.cc_list
        msg['Subject'] = self.subject
        msg.attach(body)
        
        if self.attachment:
            with open(self.attachment, 'rb') as fil:
                part = MIMEApplication(fil.read(), \
                        Name=basename(self.attachment))
                part['Content-Disposition'] = 'attachment; filename="%s"' % \
                basename(self.attachment)
                msg.attach(part)

        server = smtplib.SMTP('localhost')
        server.sendmail(self.from_list, [self.to_list, self.cc_list, self.bcc_list], msg.as_string())
        server.quit()
        self.reset()

    def print_lines(self): 
        for line in self.lines:
            print line

