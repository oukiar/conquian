<?
include("utils.php");

if(isset($_POST['devID']) )
{
    $devID = $_POST['devID'];
    $apuesta = $_POST['apuesta'];
    
    mysql_query("insert into partidas(fecha, apuesta, player1ID) values(NOW(), $apuesta, $devID)");
    
    $partID = mysql_insert_id();
    
    echo "$partID";
}
?>
