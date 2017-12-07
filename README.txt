First put the project folder in this .zip into your htdocs folder.

Next, make sure the shebang in 'index.py' points to a Python35 executable. If you're missing any packages like bcrypt or pymysql, install them with 'pip install' from your terminal (and make sure it's installing it for the right Python install by using 'where pip').

Make sure that your MySQL database has a DB called 'project' and an account called 'root' with no password (though that should be there by default) that has access to this database.

This 'project' DB needs a table called 'users' with columns:
'ID', which should be set to auto-increment and be of type INT,
'username', which should be a VARCHAR of max length at least 32, and
'password', which should also be a VARCHAR of max length at least 60 for bcrypt.

A table called 'items' with columns:
ID, same as above,
name, varchar(256),
price, int
imgurl, text
description, text
user, int, and a foreign key for the user 'ID' (from the users table) which cascades when deleted
category, an enum containing 'clothes', 'electronics', 'food', 'animals', 'furniture', 'miscellaneous'

A table called messages with columns:
ID, same as above,
subject, tinytext
sender, varchar(32), foreign key for 'username' (from users table)
recipient, same as sender,
body, text

Open the httpd.conf file (you can find it in XAMPP control panel > Apache row > Config dropdown menu > httpd.conf). Make sure that this line: "AddHandler cgi-script .cgi .pl .asp" has an extra ".py" at the end, though we can always rename 'index.py' to 'index.cgi'.

Go to the httpd-vhosts.conf file now, which isn't listed in the XAMPP control panel, but should be in "path\to\xampp\apache\conf\extra\httpd-vhosts.conf". Copy paste the following at the end of it all:

<VirtualHost *:80>
    DocumentRoot "C:/xampp/htdocs/project"
</VirtualHost>

<VirtualHost *:443>
	DocumentRoot "C:/xampp/htdocs/project"
	SSLEngine on
	SSLCertificateFile "C:\xampp\apache\conf\ssl.crt\server.crt"
	SSLCertificateKeyFile "C:\xampp\apache\conf\ssl.key\server.key"
</VirtualHost>

Make sure that the paths actually corresponds to your XAMPP installation.

It's all done and should run properly.