-- 
-- Editor SQL for DB table switches
-- Created by http://editor.datatables.net/generator
-- 

CREATE TABLE IF NOT EXISTS `switches` (
	`id` int(10) NOT NULL auto_increment,
	`switch_name` varchar(255),
	`console_ip` varchar(255),
	`active_port` varchar(255),
	`standby_port` varchar(255),
	`mgmt_ip` varchar(255),
	`switch_pwd` varchar(255),
	`power_console_detail` varchar(255),
	`switch_type` varchar(255),
	`weekday_time` varchar(255),
	`weekend_time` varchar(255),
	`hold_testbed` varchar(255),
	`user` varchar(255),
	`manager` varchar(255),
	`location` varchar(255),
	`is_sanity` varchar(255),
	`sanity_type` varchar(255),
	`sanity_sw_name` varchar(255),
	`sanity_nodes` varchar(255),
	`sanity_node_names` varchar(255),
	`start_time` datetime,
	`end_time` datetime,
	`kickstart` varchar(255),
	`system` varchar(255),
	`is_powered_on` varchar(255),
	`inactive_time` varchar(255),
	`is_sanity_activated` varchar(255),
	`linecards` varchar(255),
	`sshconsole` varchar(255),
	PRIMARY KEY( `id` )
);