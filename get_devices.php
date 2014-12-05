<?

include("utils.php");

$devID = $_POST['devID'];

$result = mysql_query("select * from dispositivos");

if($result)
{
    
    $arr = array();
    
    while($row = mysql_fetch_row($result) )
    {
        $devID = $row[0];
        $nick = $row[1];
        $lu = $row[2];
        
        $arr[$nick] = array('devID'=>$devID,
                                'lu'=>$lu);
    }
    
    echo json_encode($arr);
}
else
    echo "Error";

?>
