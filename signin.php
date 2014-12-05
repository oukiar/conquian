<?

include("utils.php");

if(isset($_POST['devID']) )
{
    $devID = $_POST['devID'];
    
    if($devID == '-1')
    {
        //insertar este nuevo dispositivo
        mysql_query("insert into dispositivos(nick, lastupdate, puntos) values('', NOW(), 100)");
        
        //datos del dipositivo
        $devID = mysql_insert_id();
        $devNick = "conquianplayer" . intval($devID);
        
        //actualizar datos de dispositivo
        mysql_query("update dispositivos set nick='$devNick' where devID=$devID");
        
        echo "SIGNUP_OK $devID";
    }
    else
    {
        //actualizar ultima actualizacion del dispositivo
        mysql_query("update dispositivos set lastupdate=NOW() where devID=$devID");
        
        //obtener nick del dispositivo
        $result = mysql_query("select nick, puntos from dispositivos where devID=$devID");
        
        if($result)
        {
            if($row = mysql_fetch_row($result))
            {
                $devNick = $row[0];
                $puntos = $row[1];
                
                echo "SIGNIN_OK " . $devNick . " " . $puntos;
            }
            else
            {
                echo "SIGNIN ERROR 2";
            }
        }
        else
        {
            echo "SIGNIN ERROR 1";
        }
    }
}
else
    echo "No post data";
?>
