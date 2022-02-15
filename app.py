import sqlite3
from flask import Flask, request, redirect, render_template, flash, url_for
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

    if request.method == 'POST':
        title = request.form['title']
        type = request.form['type']
        instructions = request.form['instructions']
        img = request.form['img']

        if not title:
            flash('Title is required')
        # elif not type:
        #     flash('Meal type is required')
        elif not instructions:
            flash('Description is required')

        else:
            conn = get_db_conn()
            conn.execute('INSERT INTO recipes (title, type, instructions, img) VALUES (?,?,?,?)', (title, type, instructions,img))
            conn.commit()
            flash('Upload Successful')
            conn.close()
            return render_template('show.html')

    return render_template('upload.html')

@app.route('/search/')
def search():
    return render_template('search.html')

@app.route('/random_recipe/', methods=('GET', 'POST'))
def random_recipe():
    # random.seed()
    # num = random.randint(0,3)
    # conn = get_db_conn()
    # recipe = conn.execute('SELECT id FROM recipes WHERE id = ?', [num]).fetchall()
    # conn.close()
    if request.method == 'POST':
        conn = get_db_conn()
        recipes = conn.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1').fetchall()
        conn.close()
        return render_template('random_recipe.html', recipes=recipes)

    conn = get_db_conn()
    recipes = conn.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1').fetchall()
    conn.close()
    return render_template('random_recipe.html', recipes=recipes)

@app.route('/show/')
def show():
    conn = get_db_conn()
    recipes = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()

    return render_template('show.html', recipes=recipes)

    # recipes = conn.execute('SELECT ingredients.description, recipes.title FROM ingredients JOIN recipes ON ingredients.recipe_id = recipe.id ORDER BY recipe.type').fetchall()

    # pairs = {}
    # key_func = lambda t: t['title']

    # for k, g in groupby(pairs, key = key_func):
    #     pairs[k] = list(g)

    # conn.close()
    # return render_template('index.html', pairs=pairs)