import pymysql; from pymysql import cursors
from flask import Flask, jsonify, render_template, url_for, redirect, Request, session
from tools import *
import bcrypt, re, random, string, os, sys

app = Flask("application")
app.config["SSL"] = True
app.config["SECRET_KEY"] = '\xf9s\xb1\xa1\xae(\xf0Z\x0c\\\xd3*\x07\x8e\xc6\xc0_\x84y\x83\xab\xc6`/\x0f6\xe7\xab%O\xb2\x99j\xbc\xe5\x99\xe1\x87\x1c.\xec,\xb0\xc6\x8bu\xb4\xe4\\\x0b\xabf\xdc\xf8:\xfa\xcdk/\xe4\xe0\xd4WF\x1b\xa6\x8e\x82\x9c(\x91\xc2\xca*\x98\x0f\xccR\x9d\xd4\xfa=\xf8\x8b\xea\xc8\xf0uG@!\x8ao\xa5Ra\\\xde\x06-Q\x8e\x9e9\xf1\xe9\xe1e\x14\xe7nU\x03J\x1f\x0e"\xa5\xb7\xfa\xb2OE\xa8A\xd0`@'
IMAGE_FOLDER = "img"
IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]
ITEM_CATEGORIES = ['clothes', 'electronics', 'food', 'animals', 'furniture', 'miscellaneous']

@app.route('/')
@ssl_required
@login_required
def renderIndex():
	return render_template('myProfile.html')

#The Mailing
@app.route('/mail', methods=['GET'])
@ssl_required
@login_required
def renderMail():
	return render_template('myMail.html')

#The Mailbox: looks in the messages database and finds all messages destined for the current user(where the recipient = current logged in user)
@app.route('/getmail', methods=['GET'])
@ssl_required
@login_required
def JSONRequestMail():
	return jsonify(getColumnsFromTable('messages', all=True,
									   where="recipient = '{}' ORDER BY `ID` DESC".format(session.get('username'))))

#Allows user to send mail to another user
#Requires: a recipient, the message body
#The title is optional
@app.route('/mail', methods=['POST'])
@ssl_required
@login_required
def receiveSendMail():
	result = {}; result['messages'] = []; result['success'] = False

	sender = session.get('username') #the sender is the current logged-in user
	recipient = request.form.get('recipient')
	subject = request.form.get('subject') or "No Subject:"
	body = request.form.get('body')

    #checks if the character limit are respected
	if len(subject) > 256:
		result['messages'].append("Subject must have at most 256 characters.")

	if len(body) > 65535:
		result['messages'].append("Message must have at most 65,535 characters.")

    #checks if receiver exists
	if not getColumnsFromTable('users', 'username', where="`username` = '{}'".format(recipient)):
		result['messages'].append("No such recipient.")

	if result['messages']:
		return jsonify(result)

	addMessageToDB(subject, sender, recipient, body) #appends the current message to messages database

	result['success'] = True

	return jsonify(result)

#access to the profile page
@app.route('/profile')
@ssl_required
@login_required
def renderProfile():
	return render_template("myProfile.html")

#the user can view their inventory containing items that they have posted
#Looks into the items database for all items where the user = current logged in user

@app.route('/inventory', methods=['GET'])
@ssl_required
@login_required
def renderInventory():
	return render_template("myInventory.html", items=getColumnsFromTable('items', all=True, where='`user` =' + str(session['uid'])))

@app.route('/getinventory', methods=['GET'])
@ssl_required
@login_required
def JSONRequestInventory():
	resp = { "items" : getColumnsFromTable('items', all=True, where='`user` =' + str(session['uid'])) }
	return jsonify(resp)

#The user can delete an item currently in their inventory.
@app.route('/deleteitem', methods=['POST'])
@ssl_required
@login_required
def receiveDeleteItem():
	resp = { 'success':False }
	try:
		id = int(request.form.get('id'))

        
		if session['uid'] != getColumnsFromTable('items', 'user', where='`id` =' + str(id))[0]['user']:
			resp['success'] = False
			return jsonify(resp)

		deleteItemFromDB(id) #deletes the item from the items database
		resp['success'] = True

	except Exception as e:
		raise e
		resp['success'] = False

	return jsonify(resp)

#The user can search for items for sale in the database
@app.route('/browse', methods=['GET'])
@ssl_required
@login_required
def renderSearchForm():
	return render_template("trade.html")

#The user can enter 3 fields to search:
#query string
#price limit
#category
@app.route('/browse', methods=['POST'])
@ssl_required
@login_required
def receiveSearchForm():
	resp = { 'items':[] }
	try:
		query = re.split('[^a-zA-Z]', request.form.get('query').lower()) #the query string
		price = int(request.form.get('price')) if request.form.get('price') else sys.maxsize #the price limit
		category = request.form.get('category') if request.form.get('category') in ITEM_CATEGORIES else "all" #the selected category, this is optional

		resp['items'] = searchItemsInDB(query, category, price) #search for the items corresponding to the user's request in the database

		for item in resp['items']:
			item['user'] = getColumnsFromTable('users', 'username', where="id = " + str(item['user']))[0]['username']

	except Exception as e:
		raise e

	return jsonify(resp)

#By logging out, the session fields are reset to None
@app.route('/logout')
@ssl_required
def renderLogout():
	session['uid'] = None
	session['username'] = None
	return redirect(removeUrlScriptRoot(url_for('renderIndex')))

#The user can post an ad of an item for sale through this functionality
#if successful added to the database, the item will show up in their inventory
@app.route('/postitem', methods=['GET'])
@ssl_required
@login_required
def renderPostItemForm():
	return render_template('myPost.html')

@app.route('/postitem', methods=['POST'])
@ssl_required
@login_required
def receiveRegisterItem():

	name = request.form.get('name') #name/title of the item
	price = int(request.form.get('price')) #asking price
	description = request.form.get('description') #item description, used in search
	category = request.form.get('category') #item category, used in search
	imgfile = request.files.get('img') #image representing the item for sale

	result = []

    #performs some checks to validate the previous fields
	if not re.match('^[\w ()]{3,256}$', name):
		result.append("Invalid name")

	if len(description) > 65535:
		result.append("Invalid description")

	if price < 0 or price.bit_length() >= 32:
		result.append("Invalid price")

	if not imgfile:
		result.append("No image")
	elif imgfile.filename.split('.', 1)[1].lower() not in IMAGE_EXTENSIONS:
		result.append("Invalid file extension")

	if category not in ITEM_CATEGORIES:
		result.append("Invalid category")

	if not result:
		registerItemToDB(name, price, description, imgfile, session.get('uid'), category)
	else:
		return jsonify(result)#Fix this, use Jinja for redirect instead.

	return redirect(removeUrlScriptRoot(url_for('renderInventory')))

#All users must be logged in to use any functionality on the website, else they will be redirected to the main page.
@app.route('/login', methods=['GET'])
@ssl_required
def renderLoginForm():
	return render_template("login.html") if session.get('uid') is None else redirect(removeUrlScriptRoot(url_for('renderPostItemForm')))

#User login, validates username and correspoding password.
@app.route('/login', methods=['POST'])
@ssl_required
def receiveLoginUser():
	username = request.form['username']
	password = request.form['password'].encode('utf-8')
	row = getColumnsFromTable('users', 'id', 'username', 'password', where="username = '" + username + "'")[0]

	onValid = lambda: redirect(removeUrlScriptRoot(url_for('renderIndex')))
	onInvalid = lambda: username + " " + password + "\n" + str(row)

	if username == row['username']:
		if bcrypt.checkpw(password, row['password'].encode('utf-8')):
			session['uid'] = row['id']
			session['username'] = row['username']
			return onValid()

	return onInvalid()

#New user registration
@app.route('/register', methods=['GET'])
@ssl_required
def renderRegisterForm():
	return render_template("register.html")

#The registration asks for two fields: username and password
#once validated, adds the new user to the database
@app.route('/register', methods=['POST'])
@ssl_required
def receiveRegisterUser():
	username = request.form['username']
	password = request.form['password']

	validuser = isValidUsername(username) #username should not already be present in database
	validpass = isValidPassword(password)

	onInvalid = lambda: redirect(removeUrlScriptRoot(url_for('renderRegisterForm')))
	onValid = lambda: redirect(removeUrlScriptRoot(url_for('renderIndex')))

	if not validuser or not validpass:
		return onInvalid()

	registerUserToDB(username, password) #updates database

    #If successful, the new user is logged in automatically
	row = getColumnsFromTable('users', 'id', where="username = '" + username + "'")[0]
	session['uid'] = row['id']
	session['username'] = username

	return onValid()

#part of the mailing system. This adds a new message into the messages database.
def addMessageToDB(subject, sender, recipient, body):
	try:
		db = getDB()
		cursor = db.cursor()

		sql = "INSERT INTO `messages`(`ID`, `subject`, `sender`, `recipient`, `body`) VALUES (NULL, %s, %s, %s, %s)"
		cursor.execute(sql, (subject, sender, recipient, body))
		db.commit()

		db.close()
	except Exception as e:
		raise e
		
#This looks for items in the items database that corresponds to the user's request according to the query, category and price entered
def searchItemsInDB(query, category, price):
	items = getColumnsFromTable('items', all=True)
	result = []
	for item in items:
		text = (item['name'] + " " + item['description']).lower()
		if item['price'] <= price and (item['category'] == category or category == "all"):
			if any(re.search(word, text) for word in query) or not query:
				result.append(item)
	return result

#If the user wishes to remove an item from their inventory.
#This deletes the selected item from the items database
def deleteItemFromDB(id):
	db = getDB()
	cursor = db.cursor()
	imgname = getColumnsFromTable('items', 'imgurl', where="`ID` = {}".format(id))[0]['imgurl'].split('/')[2]

	imgname = os.path.join(IMAGE_FOLDER, imgname)

	if os.path.isfile(imgname):
		os.remove(imgname)

	sql = "DELETE FROM `items` WHERE `id`=%s"
	cursor.execute(sql, (id))
	db.commit()
	db.close()


#Part of the registration. Adds the new user to the users database
def registerUserToDB(username, password):
	cryptpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt( 12 ))

	try:
		db = getDB()
		cursor = db.cursor()
		sql = "INSERT INTO `users`(`ID`, `username`, `password`) VALUES (NULL, %s, %s)"
		cursor.execute(sql, (username, cryptpass))
		db.commit()
		db.close()
	except Exception as e:
		raise e

#Adds requested item into the items database with its fields: name, price, description, image, category and ID
def registerItemToDB(name, price, description, imgfile, uid, category):
	try:
		db = getDB()
		cursor = db.cursor()
		sql = "INSERT INTO `items`(`ID`, `name`, `price`, `imgurl`, `description`, `user`, `category`) VALUES (NULL, %s, %s, %s, %s, %s, %s)"

		imgname = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(14))
		ext = imgfile.filename.split('.', 1)[1].lower()

		cursor.execute(sql, (name, price, '/' + IMAGE_FOLDER + '/' + imgname + '.' + ext, description, uid, category))
		db.commit()
		db.close()

		imgfile.save(os.path.join(IMAGE_FOLDER, imgname+'.'+ext))
	except Exception as e:
		raise e

#used to look up the desired database in the desired column
def getColumnsFromTable(table, *columns, all=False, where=None):
	try:
		db = getDB()
		cursor = db.cursor()

		columnsString = ""
		for col in columns:
			columnsString +=  "`"+col+"`, "
		columnsString = columnsString[:-2]

		sql = "SELECT " + ("*" if all else columnsString) + " FROM `" + table + "`"
		sql += (" WHERE " + where) if where is not None else ""
		cursor.execute(sql)
		result = cursor.fetchall()
		db.close()
		return result
	except Exception as e:
		raise e

def getDB():
	return pymysql.connect(host="localhost", user="root", password=None, db="project", cursorclass=cursors.DictCursor)

@app.errorhandler(Exception)
def renderHandleErrorDebug(e):
	import traceback

	return """<html>
	<head><title>Error Page</title></head>
	<body>
		<h2>Error</h2>
	""" + str(e) +"""
	""" + traceback.format_exc().replace("File", "<br>File") + """</body>
</html>""", 500

@app.route('/users')
def renderGetUsersJSON():
	return jsonify( {"users" : getColumnsFromTable("users", "username", "password")} )
