import sqlite3
from flask import Flask, request, redirect, render_template, url_for, session
from itertools import groupby
import time
import os


def get_ingredients_by_recipe(conn,keyword):
    '''Takes a connection to database and keyword and returns items matching keyword'''
    
    # Use keyword to get recipe ids that contain keyword
    tag = conn.execute('SELECT i.recipe_id \
        FROM ingredients i \
        JOIN recipes r \
        ON i.recipe_id = r.id \
        WHERE i.description = ?;', 
        (keyword,)).fetchall()
    
    # Grab all ingredients associated with recipes containing keyword
    items = []
    for row in range(len(tag)):
        for cell in range(len(tag[0])):
            item = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions \
                FROM ingredients i \
                JOIN recipes r \
                ON i.recipe_id = r.id \
                WHERE i.recipe_id = ? \
                ORDER BY r.title;', 
                (tag[row][cell],)).fetchall()
            items.append(item)

    return items

def group_recipe_data(items):
    '''Takes database items and maps them to recipes for html output'''
    
    # Map attributes to recipes using itertools
    recipes = {}

    key_func = lambda t:t['title']

    # groupby -> Map attributes to recipe titles
    for item in items:
        for recipe_key,recipe_group in groupby(item, key=key_func):
            recipes[recipe_key] = list(recipe_group)

    return recipes

def get_db_conn():
    '''Gets a connection to database.db and creates rows'''

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_url(file_path):
    '''Read web scraped url from extenal file'''

    with open(file_path, 'r') as url_file:
        return url_file.read()

# Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = '931349940'


#### ROUTES ####

# Index route
@app.route('/')
def index():

    return render_template('index.html')
    

##UPLOAD ROUTES##

# Upload title
@app.route('/upload-title/', methods=('GET','POST'))
def upload_title():

    if request.method == 'POST':
        conn = get_db_conn()
        session["title"] = request.form['title']
        session["type"] = request.form['type']

        conn.close()
        return redirect(url_for('upload_ingredient'))
    
    return render_template('upload-title.html')


# Upload ingredient
@app.route('/upload-ingredient/', methods=('GET','POST'))
def upload_ingredient():

    if request.method == 'POST':
        conn = get_db_conn()

        # Save uploadable content to local session storage
        session["ingredients"] = []
        session["ingredient"] = []
        session["ingredient"].append(request.form['description'])
        session["ingredient"].append(request.form['quantity'])
        session["ingredient"].append(request.form['unit'])
        session["ingredients"].append(session["ingredient"])

        conn.close()
        return redirect(url_for('upload_add_ingredient'))
    
    return render_template('upload-ingredient.html', 
    title=session["title"], 
    type=session["type"])

# Upload additional ingredients
@app.route('/upload-add-ingredient/', methods=('GET','POST'))
def upload_add_ingredient():

    if request.method == 'POST':
        conn = get_db_conn()

        session["ingredient"] = []
        session["ingredient"].append(request.form['description'])
        session["ingredient"].append(request.form['quantity'])
        session["ingredient"].append(request.form['unit'])
        session["ingredients"].append(session["ingredient"])

        conn.close()
        return redirect(url_for('upload_add_ingredient'))
    
    return render_template('upload-add-ingredient.html',
     title=session["title"], 
     type=session["type"], 
     ingredients=session["ingredients"])

# Upload instructions
@app.route('/upload-instructions/', methods=('GET','POST'))
def upload_instructions():

    if request.method == 'POST':

        conn = get_db_conn()
        session["instructions"] = request.form['instructions']
        conn.close()
        
        return redirect(url_for('gen_image'))
    
    return render_template('upload-instructions.html', 
    title=session["title"], 
    type=session["type"], 
    ingredients=session["ingredients"])

# Get Image, write keyword/read web scraped url
@app.route('/gen-image/', methods=('GET','POST'))
def gen_image():

    if request.method == 'POST':

        conn = get_db_conn()
        session["word"] = request.form['word']
        conn.close()

        # Write keyword to external file
        file_path = os.getcwd() + '/word.txt'
        with open(file_path, 'w') as word_file:
            word_file.write(session["word"])
    
        # Await url response and read in url
        file_path = os.getcwd() + '/url.txt'
        url_string = get_url(file_path)
        while url_string == '':
            time.sleep(0.5)
            url_string = get_url(file_path)
    
        # Save url to local storage
        session["url"] = url_string

        with open(file_path, 'w') as url_file:
            url_file.write('')
        
        return redirect(url_for('show_image'))


    return render_template('gen-image.html', 
    title=session["title"], 
    type=session["type"], 
    ingredients=session["ingredients"], 
    instructions=session["instructions"])

# Show image, route to database submission
@app.route('/show-image/', methods=('GET','POST'))
def show_image():

    if request.method == 'POST':
        
        return redirect(url_for('upload'))
    

    return render_template('show-image.html', 
    title=session["title"], 
    type=session["type"], 
    ingredients=session["ingredients"], 
    instructions=session["instructions"], 
    url=session["url"], )

# Upload, insert new record(s) to database
@app.route('/upload/')
def upload():
    conn = get_db_conn()

    # Insert data into recipes table
    conn.execute('INSERT INTO recipes (title, type, instructions, img) VALUES (?,?,?,?)', 
    (session["title"], session["type"], session["instructions"],session["url"]))
    conn.commit()

    # For each ingredient, insert into ingredients table and associate with recipe
    recipe_id = conn.execute('SELECT id FROM recipes WHERE title = (?)', (session["title"], )).fetchone()['id']
    for ingredient in (session["ingredients"]):
        conn.execute('INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)', 
        (ingredient[0],ingredient[1],ingredient[2],recipe_id))

    conn.commit()
    conn.close()
    return redirect(url_for('show', id=recipe_id))

# Search Route
@app.route('/search/', methods=('GET', 'POST'))
def search(keyword="*"):
    conn = get_db_conn()
    
    if request.method == 'POST':

        # Get query keyword from user, or else display everything
        keyword = request.form['keyword']
        if keyword != "*":

            # Use keyword to get recipe ids that contain keyword
            items = get_ingredients_by_recipe(conn,keyword)

        # Otherwise, Grab everything
        else:
            items = []
            item = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions \
                FROM ingredients i \
                JOIN recipes r \
                ON i.recipe_id = r.id \
                ORDER BY r.id;').fetchall()
            items.append(item)

        recipes = group_recipe_data(items)

        conn.commit()
        conn.close()
        return render_template('search.html', keyword=keyword, recipes=recipes)
    
    if keyword != "*":

        # Use keyword to get recipe ids that contain keyword
        items = get_ingredients_by_recipe(conn,keyword)

    # When nothing has been searched, default SQL search for all data using *
    else:
        items = []
        item = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions \
        FROM ingredients i \
        JOIN recipes r \
        ON i.recipe_id = r.id \
        ORDER BY r.id;').fetchall()
        items.append(item)

    recipes = group_recipe_data(items)

    conn.commit()
    conn.close()
    return render_template('search.html', recipes=recipes, keyword=keyword)

# Random Recipe Route
@app.route('/random_recipe/', methods=('GET', 'POST'))
def random_recipe():
    conn = get_db_conn()

    if request.method == 'POST':

        # Grab a random recipe from all existant recipes
        recipes = conn.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1').fetchall()

        # Get all related ingredients
        ingredients = conn.execute('SELECT * FROM ingredients i WHERE i.recipe_id = ?', 
        (recipes[0][0],)).fetchall()
        conn.close()

        return render_template('random_recipe.html', 
        recipes=recipes, ingredients=ingredients)

    # Grab a random recipe from all existant recipes
    recipes = conn.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1').fetchall()

    # Get all related ingredients
    ingredients = conn.execute('SELECT * FROM ingredients i WHERE i.recipe_id = ?', (recipes[0][0],)).fetchall()
    conn.close()
    return render_template('random_recipe.html', recipes=recipes, ingredients=ingredients)

# Recipes Route
@app.route('/recipes/')
def recipes():
    conn = get_db_conn()

    # Show all recipes in database
    recipes = conn.execute('SELECT * FROM recipes').fetchall()
    ingredients = conn.execute('SELECT * FROM ingredients').fetchall()
    conn.close()

    return render_template('recipes.html', recipes=recipes, ingredients=ingredients)

# Show Route, show one recipe based on id
@app.route('/<int:id>/show')

# route takes an id from a recipe
def show(id):
    conn = get_db_conn()

    # Get recipe that matches primary key id
    recipe = conn.execute('SELECT title, img, type, instructions FROM recipes WHERE id = ?', (id,)).fetchone()

    # Get related ingredients
    ingredients = conn.execute('SELECT * FROM ingredients i WHERE i.recipe_id = ?', (id,)).fetchall()
    conn.close()
    return render_template('show.html', recipe=recipe, ingredients=ingredients)

# Delete Route
@app.route('/<int:id>delete', methods=('POST',))

# route takes an id from a recipe
def delete(id):
    conn = get_db_conn()

    # First delete ingredients linked to recipe
    conn.execute('DELETE FROM ingredients WHERE recipe_id = ?', (id,))

    # Last delete recipe
    conn.execute('DELETE FROM recipes WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    # Redirect back to recipes route
    return redirect(url_for('recipes'))