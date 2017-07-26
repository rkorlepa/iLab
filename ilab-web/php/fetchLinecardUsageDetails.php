<?php 

    $switch_name = $_POST['SwitchName'];
    
    $db_con = mysqli_connect('172.23.152.148', 'ilab', 'nbv_12345' , 'ilab');
    if (!$db_con)
      {
      die('Could not connect: ' . mysqli_error());
      }
    //mysql_select_db('test');
    $query = "SELECT linecard, total_ports, used_ports FROM linecard_usage where switch_name = '$switch_name'";  
    //$query = "SELECT linecard, total_ports ,used_ports FROM switch_details where switch_name = '$switch_name'";
    
    $result = mysqli_query($db_con,$query); 

    if(! $result ) {
      die('Could not get data: ' . mysqli_error($db_con));
    }
    
    $encodeArr = array();
    while($row = mysqli_fetch_assoc($result)) {
        //echo "{$row['linecard']} : {$row['total_ports']} <br> ";
        //console.log(row['linecard']);
        $encodeArr[] = $row;
   }
    
    echo json_encode($encodeArr);
    mysqli_close($db_con);
?>
