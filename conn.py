import sqlite3

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS users(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT,
               pref TEXT
)
''')

connection.commit()
connection.close()