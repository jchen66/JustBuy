<?php
	function getDatabase(){
		$host = "localhost";
		$username = "root";
		$pass = NULL;
		$name = "project";
		
		$dbConnection = new mysqli($host, $username, $pass, $name) or die("Cannot connect to database");
		
		//echo("successfully connected!");
		return $dbConnection;
	}

?>
