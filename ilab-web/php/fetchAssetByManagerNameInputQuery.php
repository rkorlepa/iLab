<?php 

    $manager = $_POST['manager'];
    
    $db_con = mysqli_connect('172.23.152.148', 'ilab', 'nbv_12345', 'ilab');
    if (!$db_con)
      {
      die('Could not connect: ' . mysqli_error());
      }
    //mysql_select_db('test');
    $query = "SELECT switch_details.linecard ,COUNT( switch_details.linecard) as count FROM switch_details INNER JOIN switches ON switch_details.switch_name = switches.switch_name where switches.manager = '$manager' GROUP BY switch_details.linecard ORDER BY count DESC";  
    
    $result = mysqli_query($db_con,$query); 

    if(! $result ) {
      die('Could not get data: ' . mysqli_error($db_con));
    }
    
    $encodeArr = array();
    while($row = mysqli_fetch_assoc($result)) {
      //echo "{$row['manager']} : {$row['count']} <br> ";
        $encodeArr[] = $row;
   }
    
    echo json_encode($encodeArr);
    mysqli_close($db_con);
?>
