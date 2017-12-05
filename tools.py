from flask import current_app, redirect, request, url_for, session
from functools import wraps
import re

#Credit to Dmitry Chaplinsky (http://flask.pocoo.org/snippets/93/) for making my life easier.
def ssl_required(fn):
	@wraps(fn)
	def decorated_view(*args, **kwargs):
		if current_app.config.get("SSL"):
			if request.is_secure:
				return fn(*args, **kwargs)
			else:
				return redirect(removeUrlScriptRoot(request.url).replace("http://", "https://"), code=307)

		return fn(*args, **kwargs)

	return decorated_view

def login_required(fn):
	@wraps(fn)
	def decorated_view(*args, **kwargs):
		if session.get('uid') is not None:
			return fn(*args, **kwargs)
		else:
			return redirect(removeUrlScriptRoot(url_for('renderLoginForm')))

	return decorated_view

def isValidUsername(username):
	def CONDITIONS(username):
			return True if re.match('^\w{8,32}$', username) else False

	return True if CONDITIONS(username) else False

def isValidPassword(password):
	def CONDITIONS(password):
			return True if re.match('^\w{8,64}$', password) else False

	return True if CONDITIONS(password) else False

def removeUrlScriptRoot(url):
	return url.replace(request.script_root,'')
