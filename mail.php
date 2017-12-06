<?php
	 require 'db.php';	 
	 session_start();
	 
	 //presets username for testing
	 //$_SESSION['username'] = 'user2';
	 
	if (isset($_POST['send'])) {
		addMsg();
	}
	else if (isset($_POST['showMail'])){
		showMailbox();
	}
	else if(isset($_POST['details'])){
		viewMsg();
	}
	else if(isset($_POST['del'])){
		deleteMsg();
	}
	 	 
	function addMsg(){
		$database = getDatabase();
		$message = $_POST['msg'];
		$sender = $_SESSION['username'];
		$user = $_POST['user'];
		$subject = $_POST['subject'];
		$find = "SELECT * FROM registry where username = '$user'";

		$find_user = $database->query($find);
		
		
		if(!mysqli_fetch_array($find_user)){
			echo ("no such user exists");
		}
		
		else{
			$ID = rand(1, 999999); //generate a random ID for this messge 	
			$test = $database->query("SELECT * FROM `messages` where ID = '$ID'");
			
			while(mysqli_fetch_array($test) == true){ //re-generate the ID if it already exists
				$ID = rand(1, 999999); 
				$test = $database->query("SELECT * FROM `messages` where ID = '$ID'");
			}
			
			//echo ($user);
			//echo ("<br>");
			$insert = "INSERT INTO messages (receiver, sender, msg, ID, subject) VALUES ('$user', '$sender', '$message', '$ID', '$subject')";
			
			if($database->query($insert) === TRUE){
				echo("successfully sent! <br>");
			}
			else 
				echo("Send failed :( <br>");
		}
		
		$database->close();
	 }
	 
	 //for deleting a message from the database
	 function deleteMsg(){
		$ID = $_POST['id'];
		$database = getDatabase();
		
		$del = "DELETE FROM `messages` where ID = '$ID'";
		if($database->query($del)){
			echo("successfully deleted");
		}		
		$database->close();
		
		showMailbox();
	 }
	 
	 //generates the mailbox of the user, listing all received mails
	 function showMailbox(){
		$database = getDatabase();
		$user = $_SESSION['username'];
		$get = "SELECT * FROM `messages` where receiver = '$user'";
		$res = $database->query($get);
		
		//if(res == NULL)
		//	echo("you have no mail");
		//else{
			echo("<table>");
			echo("<tr>");
			echo("<th>Sender</th>");
			echo("<th>Subject</th>");
			echo("<th>Options</th>");
			echo("<th></th>");
			echo("<th></th>");
			echo("</tr>");
			while($row = $res->fetch_assoc()){
				$temp = $row["ID"];
				echo ("<tr>");
				echo "<td>". $row["sender"] . "</td>";
				echo "<td>". $row["subject"] . "</td>";
				echo "<td>";
				echo("<form action =\"mail.php\" method = \"POST\">"); 
				echo("<input type = \"hidden\" name = \"id\" value =\"$temp\" >");
				echo("<input type = \"submit\" value = \"See More\" name =\"details\" >");
				echo("<input type = \"submit\" value = \"Delete\" name = \"del\"><br>");
				echo "</form>";
				echo "</td>";
			}
			echo("</table>");
		//}
		
		$database->close();
	 }
	 
	 //for viewing a message in more details
	 function viewMsg(){
		$database = getDatabase();
		$ID = $_POST['id'];
		$get = "SELECT * FROM `messages` where ID = '$ID'";
		
		$res = $database ->query($get);
		$row = mysqli_fetch_array($res);
		echo("<p><b>Sender: </b> </p>");
		echo($row["sender"]);
		echo("<p> <b> Title: </b></p>");
		echo($row["subject"]);
		echo("<p> <b> Message: </b> </p>");
		echo($row["msg"]);
		
		echo("<form action =\"mail.php\" method = \"POST\">"); 
		echo("<input type = \"submit\" value = \"Back\" name = \"showMail\" ><br>");
		echo "</form>";
		
		$database->close();
	 }
	 
	//session_destroy();
	// $database->close();
	 
?>