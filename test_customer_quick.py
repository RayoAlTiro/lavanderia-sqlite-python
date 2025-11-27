from app.models.customer import Customer
from app.database import Database

# Limpiamos la base de datos (opcional, pero útil para pruebas)
# Nota: La manera más sencilla de "limpiar" es borrar y recrear la DB
# Para una prueba rápida, asumimos que ya ejecutaste el setup_db
# o simplemente borraste el archivo .db

print("Creando cliente...")
# customer_id ahora recibirá un ID > 0 (e.g., 1)
customer_id = Customer.create("Juan Perez", "4421234567", "juan@test.com")
print(f"Cliente creado ID: {customer_id}")

print("Obteniendo cliente...")
# Busca el cliente con el ID correcto
cust = Customer.get_by_id(customer_id)

# Esta línea ya no fallará porque 'cust' es ahora un objeto Customer
print("Cliente:", cust.__dict__) 

print("Listando todos...")
print(Customer.all())