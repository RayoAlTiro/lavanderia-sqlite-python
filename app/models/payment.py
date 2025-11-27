from app.database import Database
from datetime import datetime

# Nota: Se asume que 'base_model' maneja otras funcionalidades de alto nivel.
# Si solo usas la clase Customer, puedes omitir '(base_model.BaseModel)'.

db = Database()

class Payment:
    
    # CORRECCIÓN 1: Agregar id, created_at y updated_at a __init__
    def __init__(self, order_id, amount, payment, id=None, created_at=None, updated_at=None):
        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.payment = payment
        
        # Consistencia: Usar isoformat() para guardar las fechas como texto en SQLite
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat() 

    # -----------------------------
    # CREATE (ALTA)
    # -----------------------------
    @staticmethod
    def create(order_id, amount, payment):
        query = """
            -- Consistencia: Añadir campos de auditoría
            INSERT INTO payments (order_id, amount, payment, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """
        created_at = datetime.now().isoformat()
        updated_at = datetime.now().isoformat()
        
        # db.execute ya retorna el lastrowid, que es el ID de pago.
        payment_id = db.execute(query, (order_id, amount, payment, created_at, updated_at))
        return payment_id
    
    # -----------------------------
    # GET BY ID (CONSULTA)
    # -----------------------------
    @staticmethod
    def get_by_id(payment_id):
        # Aseguramos seleccionar todos los campos
        query = """
            SELECT id, order_id, amount, payment, created_at, updated_at 
            FROM payments 
            WHERE id=?
        """
        # CORRECCIÓN 2: Añadir la coma final para que (payment_id,) sea una tupla
        rows = db.fetch(query, (payment_id,)) 
        
        if not rows:
            return None
            
        r = rows[0]
        # CORRECCIÓN 3: Añadir las comas faltantes y los campos de auditoría
        return Payment(
            id=r[0],
            order_id=r[1],
            amount=r[2],
            payment=r[3],
            created_at=r[4],
            updated_at=r[5]
        )
    
    # -----------------------------
    # GET ALL (CONSULTA GENERAL)
    # -----------------------------
    @staticmethod
    def all():
        query = "SELECT id, order_id, amount, payment, created_at, updated_at FROM payments"
        rows = db.fetch(query)
        
        return [
            {
                "id": r[0],
                "order_id": r[1],
                "amount": r[2],
                "payment": r[3],
                "created_at": r[4],
                "updated_at": r[5]
            }
            for r in rows
        ]
        
    # -----------------------------
    # UPDATE (MODIFICACIÓN)
    # -----------------------------
    def update(self):
        if self.id is None:
            raise ValueError("Payment must have an ID to update.")

        self.updated_at = datetime.now().isoformat()

        query = """
            UPDATE payments
            SET order_id=?, amount=?, payment=?, updated_at=?
            WHERE id=?
        """

        db.execute(query, (self.order_id, self.amount, self.payment, self.updated_at, self.id))

    # -----------------------------
    # DELETE (BAJA)
    # -----------------------------
    def delete(self):
        if self.id is None:
            raise ValueError("Payment must have an ID to delete.")

        db.execute("DELETE FROM payments WHERE id=?", (self.id,))