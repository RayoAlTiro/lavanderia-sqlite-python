import sqlite3

class Database:
    def __init__(self, db_name="lavanderia.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def execute(self, query, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch(self, query, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows