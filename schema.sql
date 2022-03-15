-- Drop tables on startup if they exist
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS ingredients;

-- create recipe table
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    img TEXT,
    type INTEGER NOT NULL,
    instructions TEXT NOT NULL
);

-- create ingredient table
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id)
);
