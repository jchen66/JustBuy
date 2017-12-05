Okay so apparently you want to run this shit. This is how:

First pop the project folder in this .zip into your htdocs folder or some bullshit, it's aaaall the same dawg.

Next, you gotta make sure the shebang in 'index.py' points to a Python35 executable. If you're missing any packages like bcrypt or pymysql, install them with `pip install` from your terminal (and make sure it's installing it for the right Python install by using `where pip`).

Cooldawg. So now you want to make sure that your MySQL database has a DB called 'project' and an account called 'root' with no password (though that should be there by default) that has access to this database.

This 'project' DB needs (at least) a table called 'users' with columns:
`ID`, which should be set to auto-increment and be of type INT,
`username`, which should be a VARCHAR of max length at least 32, and
`password`, which should also be a VARCHAR of max length at least 60 (because bcrypt encrypts passwords into a salted hash of length at most 60 or 61, I forget.) I set it to 64 myself, but ye. Don't matter none. Done? Coolbeans.

Next, your Apache server needs to have a few config changes. Pop open the httpd.conf file (you can find it in XAMPP control panel > Apache row > Config dropdown menu > httpd.conf). Make sure that this line: "AddHandler cgi-script .cgi .pl .asp" has an extra ".py" at the end, though we can always rename 'index.py' to 'index.cgi'.

ANOTHER CONFIG CHANGE! Go to the httpd-vhosts.conf file now, which isn't listed in the XAMPP control panel, but should be in "path\to\xampp\apache\conf\extra\httpd-vhosts.conf". Copy paste the following at the end of it all:

<VirtualHost *:80>
    ##ServerAdmin webmaster@dummy-host2.example.com
    DocumentRoot "C:/xampp/htdocs/project"
    ##ServerName dummy-host2.example.com
    ##ErrorLog "logs/dummy-host2.example.com-error.log"
    ##CustomLog "logs/dummy-host2.example.com-access.log" common
</VirtualHost>

<VirtualHost *:443>
	DocumentRoot "C:/xampp/htdocs/project"
	SSLEngine on
	SSLCertificateFile "C:\xampp\apache\conf\ssl.crt\server.crt"
	SSLCertificateKeyFile "C:\xampp\apache\conf\ssl.key\server.key"
</VirtualHost>

Make sure that the paths actually corresponds to your XAMPP installation.

There's one more step: PROFIT. It's all done and should run properly.