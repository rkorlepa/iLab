<?php 
    $type_of_linecards = array();
    $db_con = mysqli_connect('172.23.152.148', 'ilab', 'nbv_12345', 'ilab');
    if (!$db_con)
      {
      die('Could not connect: ' . mysqli_error());
      }
    
    $query = "SELECT DISTINCT linecard FROM switch_details ";  
    
    $result = mysqli_query($db_con,$query); 

    if(! $result ) {
      die('Could not get data: ' . mysqli_error($db_con));
    }
    
    while($row = mysqli_fetch_assoc($result)) {
      $type_of_linecards[] = $row['linecard'];
    }


    //foreach ($type_of_linecards as $linecard_val){
        $query = "SELECT linecard,COUNT(DISTINCT switch_name) as total FROM switch_details  GROUP BY linecard ORDER BY total DESC";  
    //}

        $result = mysqli_query($db_con,$query); 

        if(! $result ) {
          die('Could not get data: ' . mysqli_error($db_con));
        }
        
        $encodeArr = array();
        while($row = mysqli_fetch_assoc($result)) {
           //echo " {$row['linecard']} :{$row['total']}  <br> ";
            $encodeArr[] = $row;
        }
        
        echo json_encode($encodeArr);

        //close the db connection
        mysqli_close($db_con);

?>
