function createTableAndPopulate(btnId,obj) {
    //console.log(obj);

        var count = 1;
        // CREATE DYNAMIC TABLE.
        var table;
        
        
        table= document.createElement("table");
        table.className += "table";
        table.className += " table-striped";
        table.className += " table-hover";
        if(btnId == "btn_usage"){
            table.setAttribute("id","UsageTable");
        }else if(btnId == "btn_asset"){
            table.setAttribute("id","inventoryTable");
        }else if(btnId == "asset_by_input"){
            table.setAttribute("id","managerTable");
        }else
            table.setAttribute("id","defaultTable");
           
        
        //table.setAttribute("data-toggle","table");
        //table.setAttribute("data-sort-name","total");
        //CREATE HTML TABLE HEADER ROW USING THE EXTRACTED HEADERS ABOVE.
        console.log(table);
       //var tr = table.insertRow(-1);                   // TABLE ROW.
        //console.log(obj);
    
        var header = table.createTHead();
        var tr = header.insertRow(-1); 
        var col = [];
    
        for(var key in obj[0]){
            col.push(key);
        }
        
        
            var th = document.createElement("th");      // TABLE HEADER.
            th.innerHTML = "#";
            //th.setAttribute("data-field","number");
            //th.setAttribute("data-sortable","true");
            tr.appendChild(th);
        for (var i = 0; i < col.length; i++) {
            th = document.createElement("th");      // TABLE HEADER.
            if(table.id == "UsageTable" && (i == 2) ){
                th.innerHTML = col[i] + "(in days)";    
            }else
                th.innerHTML = col[i];
            //th.setAttribute("data-field",col[i]);
            //th.setAttribute("data-sortable","true");
            tr.appendChild(th);
        }
    
        
        var body = table.createTBody();
        //console.log(obj.length);
        // ADD JSON DATA TO THE TABLE AS ROWS.
        for (var i = 0; i < obj.length; i++) {

            tr = body.insertRow(-1);
            var tabCell = tr.insertCell(-1);
            tabCell.innerHTML = count;
            count++;
            for (var j = 0; j < col.length; j++) {
                tabCell = tr.insertCell(-1);
                tabCell.innerHTML = obj[i][col[j]];
                //console.log(obj[i][col[j]] + " ");
                if(table.id == "UsageTable" && (j == 4) ){
                    
                    tabCell.setAttribute("data-toggle","popover");
                    tabCell.setAttribute("data-original-title","");
                    tabCell.setAttribute("title","Port Details");
                    //tabCell.setAttribute("data-content","And here's some");
                   
                   
                }
            }
            
        }
    
       

        // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
        var divContainer = document.getElementById("table-section");
        divContainer.innerHTML = "";
        divContainer.appendChild(table);
        
        sorttable.makeSortable(table);
   
    
        $(document).ready(function(){
            console.log("in popover");
            $('[data-toggle="popover"][data-original-title]').popover({
                container: 'body',
                placement: 'left',
                html:true
            })
        });
    
        $('[data-toggle="popover"][data-original-title]').click(get_data_for_popover_and_display);
       $(document).on('click', function(e) {
          $('[data-toggle="popover"],[data-original-title]').each(function() {
            //the 'is' for buttons that trigger popups
            //the 'has' for icons within a button that triggers a popup
            if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
              $(this).popover('hide').data('bs.popover').inState.click = false // fix for BS 3.3.6
            }

          });
        });

        
        $("#inventoryTable").on('click', 'td', function() {
            var Value = ($(this).text());
            fetchByAssetInput(Value);
        });
    
        $("#managerTable").on('click', 'td', function() {
            var Value = ($(this).text());
            fetchAssetByManagerNameInput(Value);
        });
    
        $("#UsageTable").on('click', 'td', function() {
            //var sw_name = ($(this).find('td').eq(1).text());
            //var user = ($(this).find('td').eq(4).text());
            console.log("event handler");
            var col = $(this).parent().children().index($(this)); 
            console.log(col);
            if(col == 4){
                console.log($(this).text());
                var sw_name = ($(this).parent('tr').find('td').eq(1).text());
                var user = ($(this).text());
                console.log(sw_name);
                fetchSwitchLocAndManager(sw_name,user);
            
            }
        });
    
    
    
        
    
}

function fetchByAssetInput(inputTxt){              
      var postData = {"AssType" : inputTxt}
      $.ajax({
        type: "POST",
        url: "../php/fetchByAssetInputQuery.php",
        data: postData,
        success:function( response ) {
            response_send = $.parseJSON(response);
            console.log(response_send);
            createTableAndPopulate("asset_by_input", response_send);
        }
       });
}


function fetchAssetByManagerNameInput(inputTxt){              
      var postData = {"manager" : inputTxt}
      $.ajax({
        type: "POST",
        url: "../php/fetchAssetByManagerNameInputQuery.php",
        data: postData,
        success:function( response ) {
            response_send = $.parseJSON(response);
            console.log(response_send);
            createTableAndPopulate("asset_by_manager", response_send);
        }
       });
}

function fetchSwitchLocAndManager(sw_name,user){
      var postData = {"SwitchName" : sw_name}
      $.ajax({
        type: "POST",
        url: "../php/fetchSwitchLocAndManagerQuery.php",
        data: postData,
        success:function( response ) {
            response = $.parseJSON(response);
            user = user + '@cisco.com';
            console.log(response[0]['location']);
            var manager = response[0]['manager']+'@cisco.com';
            var subject = sw_name + " " + response[0]['location'];
            var emailBody = 'Hey,';
            //var attach = 'path';
            document.location = "mailto:"+user+"?cc="+manager+"&subject="+subject+"&body="+emailBody;
        }
       });
}


get_data_for_popover_and_display = function() {
    console.log("in get_data_forpopover");
    var el = $(this);
    var sw_name = ($(this).parent('tr').find('td').eq(1).text());
    console.log(el.text());
    console.log(sw_name);
    var postData = {"SwitchName" : sw_name}
    $.ajax({
         type: "POST",
         url: "../php/fetchLinecardUsageDetails.php",
         data: postData,
         //dataType: 'json',
         success: function(response) {
             console.log("get_data_for_popover:data received");
             console.log(response);
             response = $.parseJSON(response);
             //console.log(response);
             htmlData = '<h5> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Linecard: &nbsp;&nbsp;&nbsp;Total &nbsp;&nbsp;Used</h5><ul>';
             for (var i = 0; i < response.length; i++) {
                 htmlData = htmlData + '<li>'+response[i]["linecard"]+ '&nbsp;&nbsp;' + response[i]["total_ports"]+ '&nbsp;&nbsp;' + response[i]["used_ports"]+ '</li>';
             }
             
             htmlData = htmlData + '</ul>';
             el.attr('data-content', htmlData);
             el.popover('show');
         }
    });
}


