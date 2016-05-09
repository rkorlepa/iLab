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
		Field::inst( 'location' )
			->validator( 'Validate::notEmpty' ),
		Field::inst( 'comments' ),
		Field::inst( 'is_sanity' )
			->validator( 'Validate::notEmpty' ),
		Field::inst( 'sanity_type' )
			->validator( function ( $var, $data, $opts ) {
				if ( preg_match("/yes/i", $data['is_sanity']) )
					if ( $var == '')
						return 'Sanity type needs to be provided';
					else
						return true;
				else
					return true;
			} ),
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
        Field::inst( 'inactive_time' ),
        Field::inst( 'is_sanity_activated' ),
        Field::inst( 'linecards' )
	)
	->process( $_POST )
	->json();


