import sqlite3 as sql


class Users:
    def __init__(self):
        self.connection = sql.connect('users.db')

    def add(self, username, password):
        with self.connection as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO ('username', 'password') VALUES ('{username}', '{password}')")

    def check_password(self, input_username, input_pasword):
        with self.connection as con:
            cur = con.cursor()
            try:
                true_username, true_password = \
                    cur.execute(f"SELECT * FROM users WHERE username == '{input_username}'").fetchone()
            except:
                raise 'User is not found'
            return true_password == input_pasword

