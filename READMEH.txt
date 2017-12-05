db.php: this file should be replaced by your own php file that has a function called getDatabase();
In your Database, you need a table called messages with the following categories:
-receiver: char of length 20
-sender: char of length 20
-msg: char of length 1000
-ID: int 
-subject: char of length 20

The mail.php also relies on another table called registry which contains the complete list of users registered on the website.
The field it checks from this table is called 'username'. It needs to check this to make sure the receiver typed in by the sender actually exists.

Feel free to change the tables name to your liking. 

For now, the username is manually set. 
Place all files into same directory. 
 
To send a message, go to the mail.html file and set the username in mail.php to the user as whom you wish to send the mail 
To view a user's mailbox, go to the mailbox.html page and set the username in mail.php to the user whose mail you wish to view 