<?php

/*
 * Editor server script for DB table switches
 * Created by http://editor.datatables.net/generator
 */

// DataTables PHP library and database connection
include( "lib/DataTables.php" );

// Alias Editor classes so they are easy to use
use
	DataTables\Editor,
	DataTables\Editor\Field,
	DataTables\Editor\Format,
	DataTables\Editor\Mjoin,
	DataTables\Editor\Upload,
	DataTables\Editor\Validate;

// The following statement can be removed after the first run (i.e. the database
// table has been created). It is a good idea to do this to help improve
// performance.
$db->sql( "CREATE TABLE IF NOT EXISTS `switches` (
	`id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
    `switch_name` varchar(255) NOT NULL DEFAULT '' COMMENT 'switch_name',
    `sshconsole` varchar(255) DEFAULT NULL,
    `mgmt_ip` varchar(255) NOT NULL COMMENT 'management ip',
    `console_ip` varchar(255) NOT NULL DEFAULT '' COMMENT 'console ip',
    `active_port` varchar(255) NOT NULL DEFAULT '' COMMENT 'active port',
    `stnd_console_ip` varchar(255) DEFAULT NULL,
    `standby_port` varchar(255) DEFAULT NULL COMMENT 'standby port',
    `console_login` varchar(255) NOT NULL DEFAULT '' COMMENT 'terminal console login details',
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
);" );

function isInteger($input) {
    return (ctype_digit(strval($input)));
}

// Build our Editor instance and process the data coming from _POST
Editor::inst( $db, 'switches', 'id' )
	->fields(
		Field::inst( 'switch_name' )
			->validator( 'Validate::notEmpty' )
			->validator( 'Validate::unique' ),
		Field::inst( 'sshconsole' ),
		Field::inst( 'console_ip' )
            ->validator( 'Validate::notEmpty' )
            ->validator( 'Validate::ip' ),
		Field::inst( 'active_port' )
            ->validator( 'Validate::notEmpty' )
            ->validator( function ( $val, $data, $opts ) {
                return isInteger($val) ? true : 'Port needs to be an integer';
            } ),
        Field::inst( 'stnd_console_ip' )
            ->validator( 'Validate::ip' )
            ->validator( function ( $val, $data, $opts) {
            	if ( $data['standby_port'] != '' ) 
            		if ( $val == '')
            			return 'This field cannot be empty as standby port is specified';
            	return true;
            } ),
		Field::inst( 'standby_port' )
            ->validator( function ( $val, $data, $opts ) {
                if ( $val == '' ) return true;
                return isInteger($val) ? true : 'Port needs to be an integer';
            } ),
        Field::inst( 'console_login' ),
		Field::inst( 'mgmt_ip' )
            ->validator( 'Validate::ip' ),
		Field::inst( 'switch_pwd' )
			->validator( 'Validate::notEmpty' ),
		Field::inst( 'power_console_detail' )
            ->validator( 'Validate::notEmpty' )
            ->validator( function ( $val, $data, $opts ) {
                if ( preg_match("/^([0-9\.]+):([0-9\,]+):(\S+):(\S+)/", $val) )
                    return true;
                else
                    return 'Format is as pdu_ip:outlets:pdu_user:pdu_pwd|... (1.2.3.4:10,11,12:admin:nbv123)';
            } ),
		Field::inst( 'switch_type' )
			->validator( 'Validate::notEmpty' ),
        Field::inst( 'weekday_time' )
            ->validator( function ( $val, $data, $opts ) {
                if ( $val == '' ) return true;
                if ( preg_match("/^\d\d:\d\d-\d\d:\d\d/", $val) )
                    return true;
                else
                    return 'Time format needs to be as (09:00-20:00)';
            } ),
		Field::inst( 'weekend_time' )
            ->validator( function ( $val, $data, $opts ) {
                if ( $val == '' ) return true;
                if ( preg_match("/^\d\d:\d\d-\d\d:\d\d/", $val) )
                    return true;
                else
                    return 'Time format needs to be as (09:00-20:00)';
            } ),
		Field::inst( 'hold_testbed' )
			->validator( 'Validate::notEmpty' ),
		Field::inst( 'user' )
			->validator( 'Validate::notEmpty' ),
		Field::inst( 'manager' ),
		Field::inst( 'project' )
			->validator( function ( $var, $data, $opts ) {
                if ( $var == '')
                    return 'Project needs to be provided';
                else
                    return true;
			} ),
		Field::inst( 'location' )
			->validator( 'Validate::notEmpty' ),
		Field::inst( 'comments' ),
		Field::inst( 'is_sanity' )
			->validator( 'Validate::notEmpty' ),
		Field::inst( 'sanity_sw_name' )
			->validator( function ( $var, $data, $opts ) {
				if ( preg_match("/yes/i", $data['is_sanity']) )
					if ( $var == '')
						return 'Sanity type needs to be provided';
					else
						return true;
				else
					return true; 
			} ),
		Field::inst( 'sanity_nodes' )
			->validator( function ( $var, $data, $opts ) {
				if ( preg_match("/yes/i", $data['is_sanity']) ) {
					if ( $var == '') return true;
					if ( isInteger($var) )
						return true;
					else
						return 'Sanity Nodes needs to be an integer or empty';
				} else {	
					if ( $var == '')
						return true;
					else
						return 'For Sanity Nodes, [is sanity] needs to be yes';
				}
			} ),
		Field::inst( 'sanity_node_names' )
			->validator( function ( $var, $data, $opts ) {
				if ( (int)$data['sanity_nodes'] > 1 ) {
					if ( $var == '' )
						return 'Sanity Node Names cannot be empty';
					else
						return true;
				} else {
					return true;
				}
			} ),
		Field::inst( 'start_time' )
			->set( false ),
		Field::inst( 'end_time' )
			->set( false ),
		Field::inst( 'kickstart' ),
        Field::inst( 'system' ),
        Field::inst( 'is_powered_on' ),
        Field::inst( 'is_sanity_activated' ),
        Field::inst( 'director' ),
        Field::inst( 'linecards' )
    )
    ->where('switch_type',$_GET['switch_type'])
    ->process( $_POST )
	->json();


