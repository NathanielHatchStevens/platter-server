from flask import Flask, render_template, request, jsonify
from flask_session import Session
from flaskext.markdown import Markdown
from flask_bcrypt import Bcrypt
import atexit
import os
import json
import sys

from dotmap import DotMap
from flask_pymongo import PyMongo

from recipetomarkdown import ParseRecipe

import routes

app = Flask(__name__, static_url_path='')
# app.config.
app.secret_key = 'DO NOT CHANGE ME; I AM A PERFECTLY ADEQUATE SECRET KEY. LOOK HOW WONDERFULLY LONG I AM. I DON\'T REALLY KNOW HOW THIS WORKS'
app.config['SESSION_TYPE'] = 'filesystem'
mongo = PyMongo(app)
Session(app)
Markdown(app)
bcrypt = Bcrypt(app)

# arg 0: filename
# arg 1: debug
# arg 2: ip
# arg 3: port

debug = False
ip = '0.0.0.0'
port = 8000

try:
	if sys.argv[1] == 'debug':
		debug = True
	
	ip = sys.argv[2]
	port = int(sys.argv[3])
except:
	pass
		
print('Debug: '+str(debug))
print('IP: ' + ip)
print('Port: ' + str(port))

localdev = False

if localdev:
	app.config['MONGO_URI'] = 'mongodb://localhost:27017/recipes'
else:
	app.config['MONGO_URI'] = 'mongodb://13.211.229.170:21017/recipes'


routes.AddRoutes(app, mongo.db, bcrypt)
		  

@atexit.register
def shutdown():
	pass
	#do shutdown stuff
	
	
if __name__ == '__main__':
	 app.run(host=ip, port=port, debug=debug)
