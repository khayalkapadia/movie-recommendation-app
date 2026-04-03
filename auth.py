from db import c, conn

def signup(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def save_preference(username, movie, liked):
    # Check if already exists
    c.execute("SELECT * FROM preferences WHERE username=? AND movie=?", (username, movie))
    result = c.fetchone()

    if result:
        # Update existing
        c.execute("UPDATE preferences SET liked=? WHERE username=? AND movie=?",
                  (liked, username, movie))
    else:
        # Insert new
        c.execute("INSERT INTO preferences VALUES (?, ?, ?)",
                  (username, movie, liked))

    conn.commit()

def get_liked_movies(username):
    c.execute("SELECT movie FROM preferences WHERE username=? AND liked=1", (username,))
    return [row[0] for row in c.fetchall()]

def remove_preference(username, movie):
    c.execute("DELETE FROM preferences WHERE username=? AND movie=?",
              (username, movie))
