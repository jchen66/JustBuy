<?php
	require 'db.php';
	
	session_start();
	
	$resp = array();
	$resp["result"] = False;
	
	if ((isset($_POST['username']) && !empty($_POST['username'])) && (isset($_POST['password']) && !empty($_POST['password']))){
		
		$username = $_POST['username'];
		$password = $_POST['password'];
		
		$db = getDatabase();
		
		$query = "SELECT `username`, `password` FROM `users` WHERE username = '{$username}'";
		
		$result = $db->query($query);
		
		if (!empty($user = $result->fetch_row())){
			if (password_verify($password, $user[1])){
				$resp["result"] = True;
				$_SESSION['username'] = $username;
			}
		}
		$db->close();
	} elseif (isset($_POST['logout']) && !empty($_POST['logout'])){
		$_SESSION['username'] = "";
	}
	
	header('Content-type: application/json');
	echo json_encode($resp);
?>