import sqlite3
import os

class Database:
    """Clase para manejar la conexión y operaciones de la base de datos SQLite."""
    def __init__(self, db_name="lavanderia.db"):
        # Obtener la ruta base (donde se encuentra el archivo database.py)
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_path, db_name)
        
        # Inicializa las tablas la primera vez que se crea la instancia
        self.initialize_tables()

    def connect(self):
        """Establece y retorna una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        # CRÍTICO: Configurar row_factory para que las consultas devuelvan resultados 
        # accesibles por nombre de columna (como si fueran diccionarios).
        conn.row_factory = sqlite3.Row 
        return conn

    def initialize_tables(self):
        """
        Crea todas las tablas necesarias si no existen. 
        Se ejecuta una sola vez durante la inicialización de la clase.
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Tabla Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT
            )
        """)
        
        # Tabla Servicios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)

        # Tabla Órdenes (Pedidos)
        # Nota: En una BD real compleja, los ítems de la orden irían en otra tabla (order_items).
        # Por ahora, usamos campos simples.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                total REAL NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                paid REAL DEFAULT 0.0,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Tabla Pagos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                method TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)
        
        conn.commit()
        conn.close()


    def execute(self, query, params=()):
        """Ejecuta una consulta de modificación (INSERT, UPDATE, DELETE) y retorna el ID insertado."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            last_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return last_id
        except sqlite3.Error as e:
            print(f"Error al ejecutar consulta: {query} - {e}")
            return None


    def fetch(self, query, params=()):
        """
        Ejecuta una consulta de lectura (SELECT) y retorna todos los resultados 
        como una lista de diccionarios (gracias a row_factory).
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            # Convertir objetos sqlite3.Row a diccionarios puros antes de retornarlos
            return [dict(row) for row in rows] 
        except sqlite3.Error as e:
            print(f"Error al ejecutar consulta: {query} - {e}")
            return []

# -------------------------------------------------------------
# INSTANCIA GLOBAL DE LA BASE DE DATOS
# Otros módulos (como Customer, Order) pueden importar y usar esta instancia.
# Al crearla aquí, también se ejecuta initialize_tables() por primera vez.
# -------------------------------------------------------------
db = Database()