import markdown as md

h1 = '# '
h2 = '## '
h3 = '### '
h4 = '#### '
h5 = '##### '
li = '* '
newline = '\n'

def MarkdownSubsection(name, subsection):
	output = '\n'
	output+= h2+name+newline
		
	for item in subsection:
		print('What is item?')
		print(item)
		output+= li+item+newline
		# if item['subheading'] == True:
			# output+= h3+item['line']+newline
		# else:
			# output+= li+item['line']+newline
			
	output+= newline
	
	return output
	

def ParseRecipe(recipe):
	output = ''
		
	# body	
	output+= MarkdownSubsection('Ingredients', recipe['ingredients'])
	output+= MarkdownSubsection('Method', recipe['method'])
	
	return output
	