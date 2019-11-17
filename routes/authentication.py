from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from dotmap import DotMap
import bcrypt

def ComparePassword(submitted, stored):
	if submitted == stored:
		return True
	else:
		return False

def AuthenticationRoutes(app, db):
	public_urls = ['/login', 
						'/register',
						'/about',
						'/create_temporary_account']

	@app.before_request
	def CheckUserAuth():
		split_path = request.path.split('/')
		
		is_public_static_file = len(split_path) >= 3 and 'public' == split_path[2]
		
		if ('id' in session):
			# print('Logged in')
			return None
		elif request.path in public_urls:
			# print('Public URL:' + request.path)
			return None
		elif is_public_static_file:
			# print('Static file:' + request.path)
			return None
		else:
			return redirect(url_for('Login'))

	@app.route('/login', methods=['GET'])
	def Login():
		if 'id' in session:
			return redirect(url_for('RecipeBook'))
		else:
			return render_template('login.html')
			
	@app.route('/login', methods=['POST'])
	def SubmitLogin():
		submission = DotMap({
			'username': request.form['username'],
			'password': request.form['password'],
			'remember_me': True if 'rememberme' in request.form else False
		})
		
		# Check username exists
		query = db.users.find_one({'name': submission.username})
		if query == None:
			flash('No such username.', 'alert-warning')
			return redirect(url_for('Login'))
		
		query = DotMap(query)
		
		match = False
		# Check password matches
		if query.pwd == submission.password:
			print("Warning: User '"+submission.username+"' is using an unhashed password.")
			match = True		
		print(query.pwd)
		print(submission.password)
		print(submission.password.encode('utf-8'))
		
		if bcrypt.checkpw(submission.password.encode('utf-8'), query.pwd) == True:
			match = True
		
		if match == False:
			flash('Incorrect password.', 'alert-warning')
			return redirect(url_for('Login'))
			#have to decode and recode into utf-8 but not sure where, shoudl also hash passwords
		
		# Save session details
		CreateSession(query._id, query.name, submission.remember_me)
		
		return redirect(url_for('RecipeBook'))		
		
		
	@app.route('/logout', methods=['GET', 'POST'])
	def logout():
		session.clear()
		return redirect(url_for('Login'))
			

	@app.route('/register', methods=['POST'])
	def register():
		username = request.form['username']
		password = request.form['password']
		
		if db.users.find_one({'name': username}) != None:
			flash('Username "'+username+'" already exists')
			return redirect(url_for('Login'))
			
		
		result = db.users.insert_one({
			'name': username,
			# 'pwd' : password
			'pwd': bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())
		})
		
		print(result)
		
		if result.acknowledged:
			CreateSession(result.inserted_id, username, False);
			return redirect(url_for('RecipeBook'))
		else:
			flash('Registration failed, website coder bad?')
			return redirect(url_for('Login'))
	
	def CreateSession(id, username, remember_me):
		session['id'] = id
		session['username'] = username
		session['permanent'] = remember_me
		
	# @app.route('/create_temporary_account', methods=['POST'])
	# def CreateTemporaryAccount():
		# cur.execute('INSERT INTO user (name, password, trial) VALUES ("temp", "Trial Account", 1)')
		# db.commit()
		# cur.execute('SELECT * FROM user ORDER BY id DESC LIMIT 1')
		# (id, _, _, _) = cur.fetchall()[0]
		
		# session['username'] = 'Trial Account'
		# session['id'] = id
		# session['trial'] = True
		
		# return redirect(url_for('AddNewRecipe'))