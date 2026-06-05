import sqlite3

cnt  = sqlite3.connect("inventory.db")
cursor = cnt.cursor()

cursor.execute("""
INSERT INTO users(username,password,role)
VALUES(?,?,?)
""", ("admin", "1234", "Admin"))

cnt.commit()

print("User Added")

cnt.close()