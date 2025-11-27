from app.database import Database

db = Database()
db.execute("DELETE FROM customers;")
print("Tabla 'customers' limpiada.")
