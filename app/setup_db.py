from app.database import Database

db = Database()

def create_tables():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            service_id INTEGER,
            date TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(service_id) REFERENCES services(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            amount REAL,
            date TEXT,
            method TEXT,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        );
        """
    ]

    for q in queries:
        db.execute(q)

if __name__ == "__main__":
    create_tables()
    print("Tablas creadas en lavanderia.db")
