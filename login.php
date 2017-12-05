<?php
	require 'db.php'
	
	if(isset($_POST['username'] && !empty($_POST['username'])) && (isset($_POST['password'] && !empty($_POST['password']))){
		
		$username = $_POST['username']
		
		$db = getDatabase();
		
		$query = "SELECT `username` FROM `users` WHERE username = '{$username}'";
		
		$result = $db->query($query);
	}
	
?>