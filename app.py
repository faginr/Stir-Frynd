from operator import ge
from pickle import GET
import sqlite3
from flask import Flask, request, redirect, render_template, flash, url_for, session
from itertools import groupby

# get connected to database.db and create rows
def get_db_conn():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = '931349940'

#### ROUTES ####

# Index route
@app.route('/')
def index():

    return render_template('index.html')
    

@app.route('/upload/', methods=('GET', 'POST'))
def upload():
    conn = get_db_conn()

    if request.method == 'POST':
        session["title"] = request.form['title']
        session["type"] = request.form['type']
        session["instructions"] = request.form['instructions']
        session["img"] = request.form['img']

        session["description"] = request.form['description']
        session["quantity"] = request.form['quantity']
        session["unit"] = request.form['unit']

        print(session["title"])

        conn.close()
        return redirect(url_for('test'))

    conn.close()
    return render_template('upload.html')

@app.route('/test/')
def test():
    print(session["title"])
    conn = get_db_conn()

    conn.execute('INSERT INTO recipes (title, type, instructions, img) VALUES (?,?,?,?)', (session["title"], session["type"], session["instructions"],session["img"]))
    conn.commit()

    recipe_id = conn.execute('SELECT id FROM recipes WHERE title = (?)', (session["title"], )).fetchone()['id']
    conn.execute('INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)', (session["description"],session["quantity"],session["unit"],recipe_id))

    conn.commit()
    conn.close()
    return redirect(url_for('show', id=recipe_id))


@app.route('/search/', methods=('GET', 'POST'))
def search(keyword="*"):
    conn = get_db_conn()
    if request.method == 'POST':
        keyword = request.form['keyword']
        if keyword != "*":
            # items = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.description = ? ORDER BY r.title;', (keyword,)).fetchall()
            tag = conn.execute('SELECT i.recipe_id FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.description = ?;', (keyword,)).fetchall()
            items = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.recipe_id = ? ORDER BY r.title;', (tag[0][0],)).fetchall()
        else:
            items = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id ORDER BY r.id;').fetchall()
        recipes = {}

        key_func = lambda t:t['title']

        for k,g in groupby(items, key=key_func):
            recipes[k] = list(g)
        conn.commit()
        conn.close()
        return render_template('search.html', recipes=recipes)
    if keyword != "*":
        tag = conn.execute('SELECT i.recipe_id FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.description= ?;', (keyword,)).fetchall()
        items = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id WHERE i.recipe_id = ? ORDER BY r.title;', (tag[0][0],)).fetchall()
    else:
        items = conn.execute('SELECT i.id, i.description, i.quantity, i.unit, r.title, r.img, r.type, r.instructions FROM ingredients i JOIN recipes r ON i.recipe_id = r.id ORDER BY r.id;').fetchall()
    recipes = {}

    key_func = lambda t:t['title']

    for k,g in groupby(items, key=key_func):
        recipes[k] = list(g)


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
    return redirect(url_for('index'))