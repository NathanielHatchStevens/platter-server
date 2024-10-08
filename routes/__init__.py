from flask import Flask, request, session, redirect, url_for, render_template, flash, Markup, jsonify, Response
import json

from bson.objectid import ObjectId

from recipetomarkdown import ParseRecipe

from .authentication import AuthenticationRoutes
# from flask_misaka import markdown

def AddRoutes(app, db):

	AuthenticationRoutes(app, db)
	
	@app.route('/server_test', methods=['POST'])
	def ServerTest():
		data = jsonify({'server_test': True})
		print('Server test returning:')
		print(data)
		return data
	
	@app.route('/about', methods=['GET'])
	def About():
		return "This is the about page"

	@app.route('/', methods=['GET'])
	@app.route('/index', methods=['GET'])
	@app.route('/recipe_book', methods=['GET'])
	def RecipeBook():
		data = {'recipes': []}
		results = db.recipes.find({'owner': session['id']})
		for r in results:
			data['recipes'].append({'name': r['title'], 'id': str(r['_id'])})
		
		return render_template('recipes.html', data = data)
		
	@app.route('/recipe/<id>', methods=['GET'])
	def Recipe(id):
		recipe = db.recipes.find_one({'owner': session['id'], '_id': ObjectId(id)})
		recipe['id'] = id
		
		if recipe == None:
			return '404: Recipe['+id+'] not found'
		
		return render_template('recipe.html', data = {'recipe': recipe})

	@app.route('/submit_recipe', methods=['POST'])
	def SubmitRecipe():
		if db.users.find_one({'_id': ObjectId(request.user_id)}) is None:
			return jsonify({'success': False})
		
		
		result = request.get_json()
		recipe = {
			'title': result['title'],
			'body': ParseRecipe(result),
			'owner': ObjectId(request.user_id),
			'url': result['url']
		}
		insert_result = db.recipes.insert_one(recipe)
		print(insert_result.inserted_id)
		return jsonify({'success': True, 'recipe_id': str(insert_result.inserted_id)})
		
	@app.route('/delete_recipe/<id>', methods=['GET'])
	def DeleteRecipe(id):
		write_concern = db.recipes.remove({'owner': session['id'], '_id': ObjectId(id)})		
		return redirect(url_for('RecipeBook'))
		
	@app.route('/edit_recipe/<id>', methods=['GET', 'POST'])
	def EditRecipe(id):
		if request.method == 'GET':
			recipe = db.recipes.find_one({'owner': session['id'], '_id': ObjectId(id)})
			return render_template('edit_recipe.html', data = {'recipe': recipe})
			
		else:
			db.recipes.update(
				{'owner': session['id'], '_id': ObjectId(id)},
				{
					'$set':{
						'title': request.form['title'],
						'body': '\n'+request.form['body']
					}
				}
			)
				
			return redirect(url_for('Recipe', id = id))