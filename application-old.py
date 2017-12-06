import pymysql; from pymysql import cursors
from flask import Flask, jsonify, render_template, url_for, redirect, Request, session
from tools import *
import bcrypt, re, random, string, os

app = Flask("application")
app.config["SSL"] = True
app.config["SECRET_KEY"] = '\xf9s\xb1\xa1\xae(\xf0Z\x0c\\\xd3*\x07\x8e\xc6\xc0_\x84y\x83\xab\xc6`/\x0f6\xe7\xab%O\xb2\x99j\xbc\xe5\x99\xe1\x87\x1c.\xec,\xb0\xc6\x8bu\xb4\xe4\\\x0b\xabf\xdc\xf8:\xfa\xcdk/\xe4\xe0\xd4WF\x1b\xa6\x8e\x82\x9c(\x91\xc2\xca*\x98\x0f\xccR\x9d\xd4\xfa=\xf8\x8b\xea\xc8\xf0uG@!\x8ao\xa5Ra\\\xde\x06-Q\x8e\x9e9\xf1\xe9\xe1e\x14\xe7nU\x03J\x1f\x0e"\xa5\xb7\xfa\xb2OE\xa8A\xd0`@'
IMAGE_FOLDER = "img"
IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]

@app.route('/')
@ssl_required
@login_required
def renderIndex():
	return render_template('myProfile.html')

@app.route('/profile')
@ssl_required
@login_required
def renderProfile():
	return render_template("myProfile.html")

@app.route('/inventory', methods=['GET'])
@ssl_required
@login_required
def renderInventory():
	return render_template("myInventory.html", items=getColumnsFromTable('items', all=True, where='`user` =' + str(session['uid'])))

@app.route('/browse', methods=['GET'])
@ssl_required
@login_required
def renderSearchForm():
	return render_template("trade.html")

@app.route('/browse', methods=['POST'])
@ssl_required
@login_required
def receiveSearchForm():
	raise Exception("receiveSearchForm not implemented.")

@app.route('/logout')
@ssl_required
def renderLogout():
	session['uid'] = None
	session['username'] = None
	return redirect(removeUrlScriptRoot(url_for('renderIndex')))

@app.route('/postitem', methods=['GET'])
@ssl_required
@login_required
def renderPostItemForm():
	return render_template('myPost.html')

@app.route('/postitem', methods=['POST'])
@ssl_required
@login_required
def receiveRegisterItem():

	name = request.form.get('name')
	price = int(request.form.get('price'))
	description = request.form.get('description')
	category = request.form.get('category')
	imgfile = request.files.get('img')

	result = ""#For debugging

	if not re.match('^[\w ()]{4,256}$', name):
		result += "Invalid name<br/>"

	if len(description) > 65535:
		result += "Invalid description.<br/>"

	if price < 0:
		result += "Invalid price.<br/>"

	if not imgfile:
		result += "No image.<br/>"
	elif imgfile.filename.split('.', 1)[1].lower() not in IMAGE_EXTENSIONS:
		result += "Invalid file extension.<br/>"

	if category not in ['clothes', 'electronics', 'food', 'animals', 'furniture', 'miscellaneous']:
		result += "Invalid category"

	#Also for debugging
	if result == "":
		registerItemToDB(name, price, description, imgfile, session.get('uid'), category)
		result = "Name: {}<br/>Price: {:.2f}<br/>Description: {}<br/>Category: {}".format(name, price, description, category)

	return result

@app.route('/login', methods=['GET'])
@ssl_required
def renderLoginForm():
	return render_template("login.html") if session.get('uid') is None else redirect(removeUrlScriptRoot(url_for('renderPostItemForm')))

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

@app.route('/register', methods=['GET'])
@ssl_required
def renderRegisterForm():
	return render_template("register.html")

@app.route('/register', methods=['POST'])
@ssl_required
def receiveRegisterUser():
	username = request.form['username']
	password = request.form['password']

	validuser = isValidUsername(username)
	validpass = isValidPassword(password)

	onInvalid = lambda: redirect(removeUrlScriptRoot(url_for('renderRegisterForm')))
	onValid = lambda: redirect(removeUrlScriptRoot(url_for('renderIndex')))

	if not validuser or not validpass:
		return onInvalid()

	registerUserToDB(username, password)

	row = getColumnsFromTable('users', 'id', where="username = '" + username + "'")[0]
	session['uid'] = row['id']
	session['username'] = username

	return onValid()

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