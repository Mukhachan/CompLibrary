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
dt_string integer NOT NULL
);