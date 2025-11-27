from app.models.service import Service

# Crear servicios de ejemplo
Service.create("Lavado", 50)
Service.create("Planchado", 40)
Service.create("Lavado y planchado", 80)

# Mostrar todos
print(Service.get_all())
