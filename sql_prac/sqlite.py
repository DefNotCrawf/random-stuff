import sqlite3 as sql
import os
import uuid

con = None
cur = None

if not os.path.exists("data.db"):
    con = sql.connect("data.db")
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS users;")
    cur.execute(
        """
        CREATE TABLE users (
            uuid TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """
    )
    con.commit()


con.close()
