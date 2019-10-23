from flask import Flask, render_template, request, jsonify
from flask_session import Session
from flaskext.markdown import Markdown
from flask_bcrypt import Bcrypt
import atexit
import os
import json

from dotmap import DotMap
from flask_pymongo import PyMongo

from recipetomarkdown import ParseRecipe

import routes

app = Flask(__name__, static_url_path='')
# app.config.
app.config['MONGO_URI'] = 'mongodb://localhost:27017/recipes'
app.secret_key = 'DO NOT CHANGE ME; I AM A PERFECTLY ADEQUATE SECRET KEY. LOOK HOW WONDERFULLY LONG I AM. I DON\'T REALLY KNOW HOW THIS WORKS'
app.config['SESSION_TYPE'] = 'filesystem'
mongo = PyMongo(app)
Session(app)
Markdown(app)
bcrypt = Bcrypt(app)

port = int(os.getenv('PORT', 80))


routes.AddRoutes(app, mongo.db, bcrypt)
		  

@atexit.register
def shutdown():
	pass
	#do shutdown stuff
	
	
if __name__ == '__main__':
	 app.run(host='0.0.0.0', port=port, debug=True)
