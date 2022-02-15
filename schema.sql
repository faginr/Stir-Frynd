-- Drop tables on startup if they exist; only for dev purposes, do not keep in final version
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS ingredients;
-- DROP TABLE IF EXISTS recipes_ingredients;

-- create recipe table
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    img TEXT,
    type INTEGER NOT NULL,
    ingredient TEXT NOT NULL,
    instructions TEXT NOT NULL
);

-- create ingredient table, for now each ingredient only goes to one recipe
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity  NOT NULL,
    unit TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id)
);

-- CREATE TABLE recipes_ingredients (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,

-- );