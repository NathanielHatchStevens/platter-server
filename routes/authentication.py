from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import bcrypt
import json
import jwt

key = 'another teirrible secret that shoudl be changed'

def ComparePassword(submitted, stored):
	if submitted == stored:
		return True
	else:
		return False

def AuthenticationRoutes(app, db):
	public_urls = ['/login', 
						'/plugin_login',
						'/register',
						'/about',
						'/create_temporary_account']

	@app.before_request
	def CheckUserAuth():
		post_json = request.get_json()
		token = None
		if post_json is not None:
			token = post_json['token'] if 'token' in post_json else None
			
		split_path = request.path.split('/')
		
		is_public_static_file = len(split_path) >= 3 and 'public' == split_path[2]
		
		if token is not None:
			decoded = jwt.decode(bytes(token[2:-1], 'utf-8'), key, algorithms=['HS256'])
			request.user_id = decoded['id']
			return None
		if ('id' in session):
			return None
		if request.path in public_urls:
			return None
		if is_public_static_file:
			return None
		
		return redirect(url_for('Login'))

	@app.route('/login', methods=['GET'])
	def Login():
		if 'id' in session:
			return redirect(url_for('RecipeBook'))
		else:
			return render_template('login.html')
			
	@app.route('/login', methods=['POST'])
	def SubmitLogin():
		submission = {
			'username': request.form['username'],
			'password': request.form['password'],
			'remember_me': True if 'rememberme' in request.form else False
		}
		
		# Check username exists
		query = db.users.find_one({'name': submission['username']})
		if query == None:
			flash('No such username.', 'alert-warning')
			return redirect(url_for('Login'))
		
		match = False
		# Check password matches
		if query['pwd'] == submission['password']:
			print("Warning: User '"+submission['username']+"' is using an unhashed password.")
			match = True
		elif bcrypt.checkpw(submission['password'].encode('utf-8'), query['pwd']) == True:
			match = True
		
		if match == False:
			flash('Incorrect password.', 'alert-warning')
			return redirect(url_for('Login'))
			#have to decode and recode into utf-8 but not sure where, shoudl also hash passwords
		
		# Save session details
		CreateSession(query['_id'], query['name'], submission['remember_me'])
		
		return redirect(url_for('RecipeBook'))		
	
	@app.route('/plugin_login', methods=['POST'])
	def PluginLogin():
		print('plugin_login')
		data = json.loads(str(request.data.decode('utf-8')))
		query = db.users.find_one({'name': data['username']})
		
		print(data)
		print(query)
		if query == None:
			return json.dumps({'success':False, 'reason':'Username not found: '+data['username']})
			
	
		if query['pwd'] == data['password'] or bcrypt.checkpw(data['password'].encode('utf-8'), query['pwd']) == True:
			token = jwt.encode({'id': str(query['_id'])}, key, algorithm='HS256')
			return json.dumps({'success':True, 'token':str(token)})
		else:
			return json.dumps({'success':False, 'reason':'Password mismatch'})
		
	@app.route('/logout', methods=['GET', 'POST'])
	def logout():
		session.clear()
		return redirect(url_for('Login'))
			

	@app.route('/register', methods=['POST'])
	def RegisterNewAccount():
		username = request.form['username']
		password = request.form['password']
		
		if db.users.find_one({'name': username}) != None:
			flash('Username "'+username+'" already exists')
			return redirect(url_for('Login'))
					
		result = db.users.insert_one({
			'name': username,
			'pwd': bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())
		})
		
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
		
	# def CheckIfLoginDetailsMatchCurrentSession(