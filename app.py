from operator import ge
from pickle import GET
import sqlite3
from flask import Flask, request, redirect, render_template, flash, url_for, session
from itertools import groupby
import time
import os

# get connected to database.db and create rows
def get_db_conn():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_url(file_path):
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
    

# @app.route('/upload/', methods=('GET', 'POST'))
# def upload():
#     conn = get_db_conn()

#     if request.method == 'POST':
#         session["title"] = request.form['title']
#         session["type"] = request.form['type']
#         session["instructions"] = request.form['instructions']
#         session["img"] = request.form['img']

#         session["description"] = request.form['description']
#         session["quantity"] = request.form['quantity']
#         session["unit"] = request.form['unit']

#         print(session["title"])

#         conn.close()
#         return redirect(url_for('test'))

#     conn.close()
#     return render_template('upload.html')

@app.route('/upload-title/', methods=('GET','POST'))
def upload_title():

    if request.method == 'POST':
        conn = get_db_conn()
        session["title"] = request.form['title']
        session["type"] = request.form['type']

        conn.close()
        return redirect(url_for('upload_ingredient'))
    
    return render_template('upload-title.html')

@app.route('/upload-ingredient/', methods=('GET','POST'))
def upload_ingredient():

    if request.method == 'POST':
        conn = get_db_conn()

        session["ingredients"] = []
        session["ingredient"] = []
        session["ingredient"].append(request.form['description'])
        session["ingredient"].append(request.form['quantity'])
        session["ingredient"].append(request.form['unit'])
        session["ingredients"].append(session["ingredient"])

        # session["description"] = request.form['description']
        # session["quantity"] = request.form['quantity']
        # session["unit"] = request.form['unit']

        conn.close()
        return redirect(url_for('upload_add_ingredient'))
    
    return render_template('upload-ingredient.html', title=session["title"], type=session["type"])

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
    
    return render_template('upload-add-ingredient.html', title=session["title"], type=session["type"], ingredients=session["ingredients"])

@app.route('/upload-instructions/', methods=('GET','POST'))
def upload_instructions():

    if request.method == 'POST':

        conn = get_db_conn()
        session["instructions"] = request.form['instructions']
        conn.close()
        
        return redirect(url_for('gen_image'))
    
    return render_template('upload-instructions.html', title=session["title"], type=session["type"], ingredients=session["ingredients"])

@app.route('/gen-image/', methods=('GET','POST'))
def gen_image():

    if request.method == 'POST':

        conn = get_db_conn()
        session["word"] = request.form['word']
        conn.close()

        file_path = os.getcwd() + '/word.txt'
        with open(file_path, 'w') as word_file:
            word_file.write(session["word"])
    
        file_path = os.getcwd() + '/url.txt'
        url_string = get_url(file_path)
        while url_string == '':
            time.sleep(0.5)
            url_string = get_url(file_path)
    
        session["url"] = url_string

        with open(file_path, 'w') as url_file:
            url_file.write('')
        
        return redirect(url_for('show_image'))


    return render_template('gen-image.html', title=session["title"], type=session["type"], ingredients=session["ingredients"], instructions=session["instructions"])

@app.route('/show-image/', methods=('GET','POST'))
def show_image():

    if request.method == 'POST':
        
        return redirect(url_for('upload'))
    

    return render_template('show-image.html', title=session["title"], type=session["type"], ingredients=session["ingredients"], instructions=session["instructions"], url=session["url"], )


@app.route('/upload/')
def upload():
    print(session["title"])
    conn = get_db_conn()

    conn.execute('INSERT INTO recipes (title, type, instructions, img) VALUES (?,?,?,?)', (session["title"], session["type"], session["instructions"],session["url"]))
    conn.commit()

    recipe_id = conn.execute('SELECT id FROM recipes WHERE title = (?)', (session["title"], )).fetchone()['id']
    for ingredient in (session["ingredients"]):
        conn.execute('INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)', (ingredient[0],ingredient[1],ingredient[2],recipe_id))

    conn.commit()
    conn.close()
    return redirect(url_for('show', id=recipe_id))


@app.route('/search/', methods=('GET', 'POST'))
def search(keyword="*"):
    conn = get_db_conn()
    if request.method == 'POST':
        keyword = request.form['keyword']
        if keyword != "*":
            tag = conn.execute('SELECT i.recipe_id FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.description = ?;', (keyword,)).fetchall()
            items = []
            for r in range(len(tag)):
                for i in range(len(tag[0])):
                    item = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.recipe_id = ? ORDER BY r.title;', (tag[r][i],)).fetchall()
                    items.append(item)
        else:
            items = []
            item = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id ORDER BY r.id;').fetchall()
            items.append(item)
        recipes = {}

        key_func = lambda t:t['title']

        for item in items:
            for k,g in groupby(item, key=key_func):
                recipes[k] = list(g)
        conn.commit()
        conn.close()
        return render_template('search.html', recipes=recipes)
    if keyword != "*":
        tag = conn.execute('SELECT i.recipe_id FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.description = ?;', (keyword,)).fetchall()
        items = []
        for r in range(len(tag)):
            for i in range(len(tag[0])):
                item = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.recipe_id = ? ORDER BY r.title;', (tag[r][i],)).fetchall()
                items.append(item)
    else:
        items = []
        item = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id ORDER BY r.id;').fetchall()
        items.append(item)
    recipes = {}

    key_func = lambda t:t['title']

    for item in items:
        for k,g in groupby(item, key=key_func):
            recipes[k] = list(g)
            print(recipes[k], list(g))


    conn.commit()
    conn.close()
    return render_template('search.html', recipes=recipes)

@app.route('/random_recipe/', methods=('GET', 'POST'))
def random_recipe():
    conn = get_db_conn()

    if request.method == 'POST':
        recipes = conn.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1').fetchall()
        print(recipes[0][0])
        ingredients = conn.execute('SELECT * FROM ingredients i WHERE i.recipe_id = ?', (recipes[0][0],)).fetchall()
        conn.close()
        return render_template('random_recipe.html', recipes=recipes, ingredients=ingredients)

    recipes = conn.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1').fetchall()
    ingredients = conn.execute('SELECT * FROM ingredients i WHERE i.recipe_id = ?', (recipes[0][0],)).fetchall()
    print(recipes[0][0])
    conn.close()
    return render_template('random_recipe.html', recipes=recipes, ingredients=ingredients)

@app.route('/recipes/')
def recipes():
    conn = get_db_conn()
    recipes = conn.execute('SELECT * FROM recipes').fetchall()
    ingredients = conn.execute('SELECT * FROM ingredients').fetchall()
    conn.close()

    return render_template('recipes.html', recipes=recipes, ingredients=ingredients)

@app.route('/<int:id>/show')
def show(id):
    conn = get_db_conn()
    recipe = conn.execute('SELECT title, img, type, instructions FROM recipes WHERE id = ?', (id,)).fetchone()
    ingredients = conn.execute('SELECT * FROM ingredients i WHERE i.recipe_id = ?', (id,)).fetchall()
    conn.close()
    return render_template('show.html', recipe=recipe, ingredients=ingredients)


@app.route('/<int:id>delete', methods=('POST',))
def delete(id):
    conn = get_db_conn()
    conn.execute('DELETE FROM ingredients WHERE recipe_id = ?', (id,))
    conn.execute('DELETE FROM recipes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('recipes'))