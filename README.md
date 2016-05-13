# iLab

This project has the details for frontend to add switches/testbed to DB and backend code for analysis.
Frontend code is developed using javascript, php and mysql.
Backend code is completely based of python and mysql.

#### Setup ilab in production

##### Requirements
1. [Apache] (http://howtoubuntu.org/how-to-install-lamp-on-ubuntu)
2. [PHP] (http://howtoubuntu.org/how-to-install-lamp-on-ubuntu)
3. [MySQL cluster] (http://galeracluster.com/downloads/)
4. [Python 2.7.11] (https://my.bluehost.com/cgi/help/python-install)
5. [HAProxy/Pen/Galera Load Balancer] (http://galeracluster.com/documentation-webpages/loadbalancing.html)
6. [Editor Datatables] (https://editor.datatables.net)

##### Extra Packages for Python
1. BeautifulSoup4
2. bs4
3. Jinja2
5. peewee
6. pexpect
7. pip
8. PyMySQL
9. prompt_toolkit
11. tablib
10. setuptools

#### Functionality

iLab currently supports to add/update/delete switches using GUI. Once added there are backend scrits which monitor the switches on daily basis to collect the inventory details, system uptime and idle time. If any discrepency in connecting to the switch throught mgmt_ip or the console ports then a recurring mail is sent to the user to correct the details of the switch.

- ilabDetails.py = Will collect the module details and other things like idle time, system up time, check password and telnet details.
- ilabPwdMail.py = Will send a mail to all the users and their respective testbeds which donot have the right switch password.
- ilabTelnetMail.py = Will send a mail to all the users and their respective testbeds which donot have the right telnet details.
