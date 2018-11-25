import sqlite3

dbname = "owdatabase.db"   

def initialise():
    conn = sqlite3.connect(dbname)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS user (
	    username Varchar NOT NULL PRIMARY KEY,
	    password Varchar NOT NULL,
	    battletag Varchar
    );''')
    conn.commit()
    conn.close()

def create_user(username, password, battletag=None):
    print(username, password, battletag)
    conn = sqlite3.connect(dbname)
    c = conn.cursor()

    c.execute(f"INSERT INTO user VALUES (?,?,?)", [username, password, battletag])
    conn.commit()
    conn.close()


def get_user(username):
    conn = sqlite3.connect(dbname)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM user WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def set_battletag(battletag, username):
    conn = sqlite3.connect(dbname)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("UPDATE user SET battletag=? WHERE username =?", [battletag, username])
    conn.commit()
    conn.close()
    

    

    
    