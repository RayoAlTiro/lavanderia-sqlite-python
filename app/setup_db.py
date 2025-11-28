from app.database import Database

def create_tables():
    db = Database()
    
    # Sentencias SQL para crear las tablas
    queries = [

        
        # Tabla CUSTOMERS
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        """,
        
        # Tabla SERVICES
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        );
        """,
        
        # Tabla ORDERS (Relación con customers y services)
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            service_id INTEGER,
            date TEXT,
            status TEXT default 'pending',
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(service_id) REFERENCES services(id)
        );
        """
        ,
        # Tabla PAYMENTS (Relación con orders) - CORREGIDA
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        );
        """
    ]
    
    # Ejecutar todas las consultas
    for query in queries:
        db.execute(query)
        
    print("Tablas creadas en lavanderia.db")

if __name__ == "__main__":
    create_tables()