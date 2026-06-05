import sqlite3

def login(username, password):
    cnt = sqlite3.connect("inventory.db")
    cursor = cnt.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()

    cnt.close()

    return user