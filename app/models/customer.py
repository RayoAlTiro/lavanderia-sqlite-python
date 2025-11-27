from app.database import Database
from datetime import datetime

db = Database()

class Customer:
    def __init__(self, name, phone=None, email=None, id=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        # Convertir a string si es objeto datetime para guardar en SQLITE
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    # -----------------------------
    # CREATE (CORREGIDO)
    # -----------------------------
    @staticmethod
    def create(name, phone=None, email=None):
        query = """
            INSERT INTO customers (name, phone, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """
        created_at = datetime.now().isoformat()
        updated_at = datetime.now().isoformat()
        
        # CORRECCIÓN: Capturamos directamente el ID retornado por db.execute()
        customer_id = db.execute(query, (name, phone, email, created_at, updated_at))
        
        return customer_id

    # -----------------------------
    # GET BY ID
    # -----------------------------
    @staticmethod
    def get_by_id(customer_id):
        query = "SELECT id, name, phone, email, created_at, updated_at FROM customers WHERE id=?"
        rows = db.fetch(query, (customer_id,))

        if not rows:
            return None # Retorna None si no hay resultados
        
        # El código de mapeo es correcto, se adapta a las 6 columnas
        r = rows[0]
        return Customer(
            id=r[0],
            name=r[1],
            phone=r[2],
            email=r[3],
            created_at=r[4],
            updated_at=r[5]
        )

    # -----------------------------
    # GET ALL
    # -----------------------------
    @staticmethod
    def all():
        rows = db.fetch("SELECT id, name, phone, email, created_at, updated_at FROM customers")

        return [
            {
                "id": r[0],
                "name": r[1],
                "phone": r[2],
                "email": r[3],
                "created_at": r[4],
                "updated_at": r[5]
            }
            for r in rows
        ]

    # -----------------------------
    # UPDATE
    # -----------------------------
    def update(self):
        if self.id is None:
            raise ValueError("Customer must have an ID to update.")

        self.updated_at = datetime.now().isoformat()

        query = """
            UPDATE customers
            SET name=?, phone=?, email=?, updated_at=?
            WHERE id=?
        """
        
        # db.execute(query) retorna el ID de la fila (self.id), lo cual es útil para verificar
        db.execute(query, (self.name, self.phone, self.email, self.updated_at, self.id))

    # -----------------------------
    # DELETE
    # -----------------------------
    def delete(self):
        if self.id is None:
            raise ValueError("Customer must have an ID to delete.")

        db.execute("DELETE FROM customers WHERE id=?", (self.id,))