<?php
    
    $db_con = mysqli_connect('172.23.152.148', 'ilab', 'nbv_12345' , 'ilab');
    if (!$db_con)
      {
      die('Could not connect: ' . mysqli_error());
      }
    
     $query = "SELECT switch_status.switch_name, switches.switch_type, switch_status.idle_time ,switches.user FROM switch_status INNER JOIN 
     switches ON switch_status.switch_name = switches.switch_name";  
    
    $result = mysqli_query($db_con,$query); 

    if(! $result ) {
      die('Could not get data: ' . mysqli_error($db_con));
    }
    

    $query = "SELECT switch_name, SUM(total_ports) as total, SUM(used_ports) as used FROM linecard_usage GROUP BY switch_name";  
    $result_ports = mysqli_query($db_con,$query); 

    if(! $result_ports ) {
      die('Could not get data: ' . mysqli_error($db_con));
    }
        
    $encodeArr = array();
    while($row = mysqli_fetch_assoc($result)) {
        $encodeArr[] = $row;
    }
    
    $encodeArr_ports = array();
    while($row_ports = mysqli_fetch_assoc($result_ports)){
          $encodeArr_ports[] = $row_ports;  
    }

    foreach($encodeArr as $i => $item) {
        $flag = 0;
        foreach($encodeArr_ports as $j => $item_ports) {
            
            if($encodeArr[$i]['switch_name'] == $encodeArr_ports[$j]['switch_name']){
                $encodeArr[$i]['total_ports'] = $encodeArr_ports[$j]['total'];
                $encodeArr[$i]['used_ports'] = $encodeArr_ports[$j]['used'];
                $flag = 1;
                break;
            }
            
        }
       if($flag == 0){
            $encodeArr[$i]['total_ports'] = 0;
            $encodeArr[$i]['used_ports'] = 0;
        }
        if(strpos($encodeArr[$i]['idle_time'], ',')){
            $myArray = explode(',', $encodeArr[$i]['idle_time']);
            $myArray = explode(" ", $myArray[0]);
            $encodeArr[$i]['idle_time'] = $myArray[0];
        }else
            $encodeArr[$i]['idle_time'] = "0";
        
    }
    echo json_encode($encodeArr);

    //close the db connection
    mysqli_close($db_con);
?>
