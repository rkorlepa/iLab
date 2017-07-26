<?php 

    $input_date = $_POST['Date'];
    $new_date = date('Y-m-d', strtotime($_POST['Date']));
    //echo $new_date;
    $db_con = mysqli_connect('172.23.152.148', 'ilab', 'nbv_12345' , 'ilab');
    if (!$db_con)
      {
      die('Could not connect: ' . mysqli_error());
      }
    //mysql_select_db('test');
    $query = "SELECT switch_name, user, manager,timestamp, updated_at FROM switches where timestamp >= '$new_date' ";  
    
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
