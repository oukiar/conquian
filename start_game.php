<?
include("utils.php");

if(isset($_POST['devID']) )
{
    $devID = $_POST['devID'];
    
    $result = mysql_query("select MIN(partID) from partidas where apuesta='1' and
                                                                    (player2ID = 0 or
                                                                    player3ID = 0 or
                                                                    player4ID = 0 ) 
                                                                    
                                                                     ");
    
    $row = mysql_fetch_row($result);
    
    if( $row[0] != NULL )
    {
        $partID = $row[0];
        
        #jugadores actuales
        $result = mysql_query("select player1ID, player2ID, player3ID, player4ID from partidas where partID=$partID");
        
        
        if($row = mysql_fetch_row($result) )
        {
            $player1ID = $row[0];
            $player2ID = $row[1];
            $player3ID = $row[2];
            $player4ID = $row[3];
            
            if($player2ID == 0)
            {
                mysql_query("update partidas set player2ID=$devID where partID=$partID");
            }
            else if($player3ID == 0)
            {
                mysql_query("update partidas set player3ID=$devID where partID=$partID");
            }
            else if($player4ID == 0)
            {
                mysql_query("update partidas set player4ID=$devID where partID=$partID");
            }
            
            echo json_encode(array("partID"=>$partID, 'player1ID'=>$player1ID,
                                                        'player2ID'=>$player2ID,
                                                        'player3ID'=>$player3ID,
                                                        'player4ID'=>$player4ID ) );
        }
        else
        {
            echo "ERROR_SELECCIONANDO_PLAYERS, $partID";
        }
    }
    else
    {
        //crear nueva partida
        mysql_query("insert into partidas(fecha, apuesta, player1ID) values(NOW(), 1, $devID)");
            
        $partID = mysql_insert_id();

        echo json_encode(array("partID"=>$partID, 'player1ID'=>$devID,
                                                'player2ID'=>'0',
                                                'player3ID'=>'0',
                                                'player4ID'=>'0' ));

    }
    
}
?>
