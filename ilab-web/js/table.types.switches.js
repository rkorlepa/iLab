/*
 * Editor client script for DB table switches
 * Created by http://editor.datatables.net/generator
 */

function findGetParameter(parameterName) {
    var result = null,
        tmp = [];
    var items = location.search.substr(1).split("&");
    for (var index = 0; index < items.length; index++) {
        tmp = items[index].split("=");
        if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
    }
    return result;
}

var switch_type = findGetParameter('type'); 

// swtype field type plug-in code
(function ($, DataTable) {

if ( ! DataTable.ext.editorFields ) {
    DataTable.ext.editorFields = {};
}

var Editor = DataTable.Editor;
var _fieldTypes = DataTable.ext.editorFields;

_fieldTypes.swtype = {
	create: function ( conf ) {
		var that = this;

		conf._enabled = true;

		// Create the elements to use for the input
		conf._input = $(
			'<div id="'+Editor.safeId( conf.id )+'">'+
				'<button class="inputButton" value="' + switch_type + '">' + switch_type + '</button>'+
			'</div>');

		// Use the fact that we are called in the Editor instance's scope to call
		// the API method for setting the value when needed
		$('button.inputButton', conf._input).click( function () {
			if ( conf._enabled ) {
				that.set( conf.name, $(this).attr('value') );
			}

			return false;
		} );

		return conf._input;
	},

	get: function ( conf ) {
		return $('button.selected', conf._input).attr('value');
	},

	set: function ( conf, val ) {
		$('button.selected', conf._input).removeClass( 'selected' );
		$('button.inputButton[value='+val+']', conf._input).addClass('selected');
	},

	enable: function ( conf ) {
		conf._enabled = true;
		$(conf._input).removeClass( 'disabled' );
	},

	disable: function ( conf ) {
		conf._enabled = false;
		$(conf._input).addClass( 'disabled' );
	}
};

_fieldTypes.yesno = {
	create: function ( conf ) {
		var that = this;

		conf._enabled = true;

		// Create the elements to use for the input
		conf._input = $(
			'<div id="'+Editor.safeId( conf.id )+'">'+
				'<button class="inputButton" value="yes">yes</button>'+
				'<button class="inputButton" value="no">no</button>'+
			'</div>');

		// Use the fact that we are called in the Editor instance's scope to call
		// the API method for setting the value when needed
		$('button.inputButton', conf._input).click( function () {
			if ( conf._enabled ) {
				that.set( conf.name, $(this).attr('value') );
			}

			return false;
		} );

		return conf._input;
	},

	get: function ( conf ) {
		return $('button.selected', conf._input).attr('value');
	},

	set: function ( conf, val ) {
		$('button.selected', conf._input).removeClass( 'selected' );
		$('button.inputButton[value='+val+']', conf._input).addClass('selected');
	},

	enable: function ( conf ) {
		conf._enabled = true;
		$(conf._input).removeClass( 'disabled' );
	},

	disable: function ( conf ) {
		conf._enabled = false;
		$(conf._input).addClass( 'disabled' );
	}
};

})(jQuery, jQuery.fn.dataTable);

(function($){

$(document).ready(function() {
	var editor = new $.fn.dataTable.Editor( {
		ajax: '../php/table.types.switches.php?switch_type=' + switch_type,
		table: '#switches',
		fields: [
			{
				"label": "<font color=\"#109e37\"><b>Switch Name</b></font>",
				"name": "switch_name",
				"fieldInfo": "Switch Name, can be any random name but unique one"
			},
			{
				"label": "<font color=\"#109e37\"><b>Active Console IP</b></font>",
				"name": "console_ip",
				"fieldInfo": "Active terminal Server IP"
			},
			{
				"label": "<font color=\"#109e37\"><b>Active Port</b></font>",
				"name": "active_port",
				"fieldInfo": "Port connected from active terminal server"
			},
			{
				"label": "<font color=\"#109e37\"><b>Mgmt IP</b></font>",
				"name": "mgmt_ip",
				"fieldInfo": "IP allocated to 'interface mgmt0' in default vdc"
			},
			{
				"label": "<font color=\"#109e37\"><b>Switch Pwd</b></font>",
				"name": "switch_pwd",
				"fieldInfo": "Switch/Testbed password"
			},
			{
				"label": "<font color=\"#109e37\"><b>Location</b></font>",
				"name": "location",
				"fieldInfo": "Location which is written on ceiling in Lab<br>Eg: sjc06-104-pp10"
			},
			{
				"label": "<font color=\"#109e37\"><b>User</b></font>",
				"name": "user",
				"fieldInfo": "Username of the person using this switch"
			},
			{
				"label": "<font color=\"#109e37\"><b>Switch Type</b></font>",
				"name": "switch_type",
				"type": "swtype",
                "def" : switch_type 
			},
			{
				"label": "<font color=\"#109e37\"><b>Project</b></font>",
				"name": "project",
                "fieldInfo": "The project to which this testbed is allocated"
			},
			{
				"label": "Hold Switch",
				"name": "hold_testbed",
				"type": "yesno",
				"def": 'no',
			},
			{
				"label": "Proxy Server IP",
				"name": "sshconsole",
				"fieldInfo": "The private network IP behind which the testbed is accessible<br>Eg: johnxy:admin:pwd | 10.10.10.10:admin:pwd"
			},
			{
				"label": "StandbOy Console IP",
				"name": "stnd_console_ip",
				"fieldInfo": "Standby terminal server IP"
			},
			{
				"label": "Standby_port",
				"name": "standby_port",
				"fieldInfo": "Port connected from standby terminal server"
			},
			{
				"label": "Weekday Time",
				"name": "weekday_time",
				"def": '09:00-19:00',
				"fieldInfo": "Time when the switch is actively used"
			},
			{
				"label": "Weekend Time",
				"name": "weekend_time",
				"fieldInfo": "Time when the switch is actively used"
			},
			{
				"label": "Power Console",
				"name": "power_console_detail",
				"def": "0.0.0.0:0:x:x",
				"fieldInfo": "PDUip:outlets:PDUlogin:PDUpwd <br>(Leave it as is if not known)"
			},
			{
				"label": "Comments",
				"name": "comments"
			},
			{
				"label": "Is Sanity",
				"name": "is_sanity",
				"type": "yesno",
				"def": 'no'
			},
			{
				"label": "Sanity Testbed Name",
				"name": "sanity_sw_name",
				"fieldInfo": "Applicable only when Is Sanity is YES"
			},
			{
				"label": "Sanity Nodes",
				"name": "sanity_nodes",
				"fieldInfo": "Applicable only when Is Sanity is YES. How many node setup is this"
			},
			{
				"label": "Sanity Node Names",
				"name": "sanity_node_names",
				"fieldInfo": "Applicable only when Is Sanity is YES. The other sanity testbed names its attached to."
			},
			{
				"label": "is_powered_on",
				"name": "is_powered_on",
				"type": "hidden",
				"def": "on"
			},
			{
				"label": "console_login",
				"name": "console_login",
				"type": "hidden",
				"def": "admin:nbv123"
			}
		]
	} );

	// ActOivate the bubble editor on click of a table cell
    $('#switches').on( 'click', 'tbody td.editable', function (e) {
        editor.inline( this, {
            submit: 'allIfChanged'
        } );
    } );

	var table = $('#switches').DataTable( {
		dom: 'Bfrtip',
		ajax: '../php/table.types.switches.php?switch_type=' + switch_type,
		scrollX: true,
		columns: [
            {
            	"className": 'select-checkbox',
                "orderable": false,
                "data": null,
                "defaultContent": ''
            },
            {
                "className":      'details-control',
                "orderable":      false,
                "data":           null,
                "defaultContent": ''
            },
			{ "data": "switch_name" },
			{ 
				"data": null, 
                "render": function ( data, type, row ) {
                	if(data.stnd_console_ip == null) {
                		return data.console_ip
                	} else {
                		return data.console_ip+'&nbsp;|&nbsp;'+data.stnd_console_ip
                	}
                }
            },
            { 
                "data": null, 
                "render": function ( data, type, row ) {
                    return data.active_port+'&nbsp;|&nbsp;'+data.standby_port
                }
            },
			{ "data": "mgmt_ip" },
			{ "data": "switch_type" },
			{ "data": "weekday_time", "className": "editable"},
			{ "data": "project" },
			{ 
                "data": null,
                "render": function ( data, type, row ) {
                    if(data.linecards == null)
                        return "";
                    else
                        return data.linecards.replace(/,/g, "<br>");
                }
            },
			{ 
                "data": null,
                "render": function ( data, type, row ) {
                    if(data.user == null)
                        return "";
                    else
                        return data.user.replace(/,/g, "<br>");
                }
            },
			{ 
                "data": null, 
                "render": function ( data, type, row ) {
                    if(data.manager == null)
                        return "";
                    else
                        return data.manager.replace(/,/g, "<br>");
                }
            }
		],
		select: 
		{
            style:    'os',
            selector: 'td:first-child'
		},
		lengthChange: false,
		buttons: [
			{ extend: 'create', editor: editor },
			{ extend: 'edit',   editor: editor },
			{
                extend: "remove", 
                editor: editor,
                formMessage: function ( e, dt ) { 
                    var rows = dt.rows( e.modifier() ).data().pluck('switch_name');
                    return 'Are you sure you want to delete the switch?'+
                        	'<ul><li>'+rows.join()+'</li></ul>';
                }   
            }
		]
	} );

	function format ( d ) {
	    // `d` is the original data object for the row
	    return '<table class="extra" cellpadding="5" cellspacing="0" border="0" style="padding-left:25px;">'+
	        '<tr>'+
	            '<td>Weekend Time:</td>'+
	            '<td>'+d.weekend_time+'</td>'+
	        '</tr>'+
	        '<tr>'+
	            '<td>Power Console:</td>'+
	            '<td>'+d.power_console_detail+'</td>'+
	        '</tr>'+
	        '<tr>'+
	            '<td>Location:</td>'+
	            '<td>'+d.location+'</td>'+
	        '</tr>'+
	    '</table>';
	}

	$('#switches tbody').on('click', 'td.details-control', function () {
		var tr = $(this).closest('tr');
        var row = table.row( tr );
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
        	// Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
		}
	} );
} );

}(jQuery));

