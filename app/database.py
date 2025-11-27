import sqlite3
import os

class Database:
    def __init__(self, db_name="lavanderia.db"):
        # Esto asegura que la DB se cree en la carpeta 'app'
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_path, db_name)

    def connect(self):
        return sqlite3.connect(self.db_path)

    def execute(self, query, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        
        # CORRECCIÓN: Capturamos el ID inmediatamente después de la ejecución.
        last_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return last_id

    def fetch(self, query, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        return rows