CREATE TABLE IF NOT EXISTS mainmenu (
    id integer PRIMARY KEY AUTOINCREMENT,
    title next NOT NULL,
    url text NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    author text NOT NULL,
    year integer NOT NULL,
    number integer NOT NULL,
    descript text NOT NULL,
    dt_string integer NOT NULL,
    book_picture text NULL
);

CREATE TABLE IF NOT EXISTS placeholder (
    id integer PRIMARY KEY AUTOINCREMENT,
    class text NOT NULL,
    name text NOT NULL,
    type text NOT NULL,
    placeholder text NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id integer PRIMARY KEY AUTOINCREMENT,
    email text NOT NULL,
    card integer NOT NULL,
    password integer NOT NULL
);
CREATE TABLE IF NOT EXISTS book_history (
    id_instance integer NOT NULL,
    user_id integer NOT NULL,
    dt_string integer NOT NULL,
    action text NOT NULL
)