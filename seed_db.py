import sqlite3

# create database file
connection = sqlite3.connect('database.db')

# open and read schema, cue for executing sql commands
with open('schema.sql') as file:
    connection.executescript(file.read())

# create cursor object
cur = connection.cursor()

# execute initial sql commands, seed the database

# #### Recipes ####
cur.execute("INSERT INTO recipes (title, img, type, instructions) VALUES (?,?,?,?)", (
    'Oatmeal', 
    'https://images.unsplash.com/photo-1614961234488-3c1ac5c28ef1?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=350&q=300',
    0,
    'Step 1: Bring hot water to a boil.\
     Step 2: pour water over oats. Enjoy!'))
cur.execute("INSERT INTO recipes (title, img, type, instructions) VALUES (?,?,?,?)", (
    'Grilled Cheese',
    'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=350&q=300',
    1,
    'Step 1: Heat pan to medium high.\
    Step 2: Place cheese between bread.\
    Step 3: Place sandwich in pan for 2 minutes. \
    Step 4: Flip sandwich to fry other side.\
    Step 5: Remove sandwich, cut and enjoy!'))
cur.execute("INSERT INTO recipes (title, img, type, instructions) VALUES (?,?,?,?)", (
    'Roasted Chicken',
    'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=350&q=300',
    2,
    'Step 1: Preheat Oven to 350 degree F.\
    Step 2: Rub chicken with spices.\
    Step 3: Put chicken on baking sheet in oven for 45 minutes\
    Step 4: Remove chicken and rest 5 minutes before cutting.'))

# #### Ingredinets ####
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Oats',
    1,
    'half cup',
    1))
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Hot Water',
    1,
    'cup',
    1))
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Salt',
    1,
    'pinch',
    1))
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Cheese',
    2,
    'slices',
    2))
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Bread',
    2,
    'slices',
    2))
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Chicken',
    1,
    'whole',
    3))
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Salt',
    1,
    'pinch',
    3))
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Pepper',
    1,
    'pinch',
    3))
cur.execute("INSERT INTO ingredients (description, quantity, unit, recipe_id) VALUES (?,?,?,?)", (
    'Thyme',
    1,
    'pinch',
    3))

# commit changes, close connection
connection.commit()
connection.close()
    