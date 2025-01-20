import sqlite3
from itertools import product


def initiate_db():
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products(
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users(
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                balance INTEGER NOT NULL
            );
        ''')
        connection.commit()
    connection.close()


def get_add_products(id, title, description, price):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    check_user = cursor.execute("SELECT * FROM Products WHERE id=?", (id,))

    if check_user.fetchone() is None:
        cursor.execute(f'''
    INSERT INTO Products VALUES('{id}', '{title}', '{description}', '{price}')
''')
    connection.commit()
    connection.close()


def get_all_products(cursor=None):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Products")
    total = cursor.fetchall()
    for prod in total:
        print(prod)
    return total
    connection.commit()
    connection.close()


def add_user(username, email, age):
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO Users (username, email, age, balance) 
            VALUES (?, ?, ?, 1000);
        ''', (username, email, age))
        connection.commit()


def is_included(username):
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
        return cursor.fetchone() is not None
