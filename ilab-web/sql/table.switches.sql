-- 
-- Editor SQL for DB table switches
-- Created by http://editor.datatables.net/generator
-- 

CREATE TABLE IF NOT EXISTS `switches` (
    `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
    `switch_name` varchar(255) NOT NULL DEFAULT '' COMMENT 'switch_name',
    `sshconsole` varchar(255) DEFAULT NULL,
    `mgmt_ip` varchar(255) NOT NULL COMMENT 'management ip',
    `console_ip` varchar(255) NOT NULL DEFAULT '' COMMENT 'console ip',
    `active_port` varchar(255) NOT NULL DEFAULT '' COMMENT 'active port',
    `stnd_console_ip` varchar(255) DEFAULT NULL,
    `standby_port` varchar(255) DEFAULT NULL COMMENT 'standby port',
    `console_login` varchar(255) DEFAULT NULL COMMENT 'terminal console login details',
    `switch_pwd` varchar(255) NOT NULL DEFAULT '' COMMENT 'switch pwd',
    `power_console_detail` varchar(255) NOT NULL DEFAULT '' COMMENT 'APC/PDU details',
    `switch_type` varchar(255) NOT NULL DEFAULT '' COMMENT 'type of switch',
    `weekday_time` varchar(255) DEFAULT NULL COMMENT 'weekday use time',
    `weekend_time` varchar(255) DEFAULT NULL COMMENT 'weekend use time',
    `hold_testbed` varchar(255) NOT NULL DEFAULT '' COMMENT 'hold it',
    `user` varchar(255) NOT NULL DEFAULT '' COMMENT 'email of user',
    `manager` varchar(255) DEFAULT '',
    `project` varchar(255) DEFAULT NULL COMMENT 'which sanity',
    `location` varchar(255) NOT NULL DEFAULT '' COMMENT 'location of switch',
    `sanity_sw_name` varchar(255) DEFAULT NULL COMMENT 'switch name in sanities',
    `sanity_nodes` varchar(255) DEFAULT NULL COMMENT 'how many sanity nodes',
    `sanity_node_names` varchar(255) DEFAULT NULL COMMENT 'which nodes is it connected to',
    `start_time` datetime DEFAULT '0000-00-00 00:00:00' COMMENT 'everyday start time',
    `end_time` datetime DEFAULT '0000-00-00 00:00:00' COMMENT 'everyday end time',
    `kickstart` varchar(255) DEFAULT NULL COMMENT 'kick image',
    `system` varchar(255) DEFAULT NULL COMMENT 'sys image',
    `is_powered_on` varchar(255) DEFAULT NULL COMMENT 'state of switch',
    `is_sanity` varchar(255) DEFAULT NULL COMMENT 'is sanity compatible',
    `is_sanity_activated` varchar(255) DEFAULT NULL COMMENT 'is sanity activated',
    `linecards` varchar(255) DEFAULT NULL COMMENT 'line card values',
    `comments` varchar(255) DEFAULT NULL,
    `director` varchar(255) DEFAULT NULL COMMENT 'testbed unde which director',
    `timestamp` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'time when added',
    PRIMARY KEY (`id`)
);
