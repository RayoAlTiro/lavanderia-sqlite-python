import sqlite3
import os
# Importamos datetime para usarlo en la inicialización si fuera necesario, aunque es mejor en los modelos.
# from datetime import datetime 

class Database:
    """Clase para manejar la conexión y operaciones de la base de datos SQLite."""
    def __init__(self, db_name="lavanderia.db"):
        # Obtener la ruta base (donde se encuentra el archivo database.py)
        # Esto ayuda a que la BD se cree o encuentre en la ubicación correcta
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_path, db_name)

    def connect(self):
        """Establece y retorna una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        # CRÍTICO: Configurar row_factory para que las consultas devuelvan resultados accesibles por nombre de columna
        conn.row_factory = sqlite3.Row 
        return conn

    def execute(self, query, params=()):
        """Ejecuta una consulta de modificación (INSERT, UPDATE, DELETE) y retorna el ID insertado."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id

    def fetch(self, query, params=()):
        """
        Ejecuta una consulta de lectura (SELECT) y retorna todos los resultados 
        como una lista de diccionarios.
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        # Convertir objetos sqlite3.Row a diccionarios puros antes de retornarlos
        return [dict(row) for row in rows] 

# -------------------------------------------------------------
# ESTA ES LA LÍNEA CRÍTICA QUE SOLUCIONA EL ImportError
# Crea la instancia global 'db' para que otros módulos puedan importarla.
# -------------------------------------------------------------
db = Database()