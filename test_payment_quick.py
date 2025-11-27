from app.models.payment import Payment
from datetime import datetime

print("--- PRUEBA DE PAGO ---")

# 1. Crear un pago de prueba
# Usamos order_id=1, monto=50.50, tipo='Efectivo'
print("Creando pago...")
payment_id = Payment.create(
    order_id=1, 
    amount=50.50, 
    payment="Efectivo"
)
print(f"Pago creado ID: {payment_id}")


# 2. Obtener el pago por ID
print("Obteniendo pago por ID...")
pay = Payment.get_by_id(payment_id)

if pay:
    # Verificamos que sea una instancia de Payment y mostramos sus atributos
    print("Pago obtenido:")
    print(f"  ID: {pay.id}")
    print(f"  Order ID: {pay.order_id}")
    print(f"  Monto: {pay.amount}")
    print(f"  Tipo: {pay.payment}")
    print(f"  Creado en: {pay.created_at}")
else:
    print("Error: No se pudo obtener el pago.")


# 3. Listar todos los pagos
print("\nListando todos los pagos...")
all_payments = Payment.all()
print(f"Total de pagos en DB: {len(all_payments)}")

if all_payments:
    # Muestra el primer pago en formato de diccionario
    print("Primer pago listado:")
    print(all_payments[0]) 

print("----------------------")