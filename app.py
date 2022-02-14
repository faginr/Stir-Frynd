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
    # conn = get_db_conn()
    # recipes = conn.execute('SELECT ingredients.description, recipes.title FROM ingredients JOIN recipes ON ingredients.recipe_id = recipe.id ORDER BY recipe.type').fetchall()

    # pairs = {}
    # key_func = lambda t: t['title']

    # for k, g in groupby(pairs, key = key_func):
    #     pairs[k] = list(g)

    # conn.close()
    # return render_template('index.html', pairs=pairs)

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/random')
def random():
    return render_template('random.html')

@app.route('/show')
def show():
    return render_template('show.html')