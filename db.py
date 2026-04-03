import sqlite3

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
''')

# Preferences table
c.execute('''
CREATE TABLE IF NOT EXISTS preferences(
    username TEXT,
    movie TEXT,
    liked INTEGER
)
''')
