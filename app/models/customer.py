from app.database import db # ¡Ahora funciona!
from datetime import datetime

class Customer:
    """Modelo de Cliente."""
    def __init__(self, name, phone=None, email=None, id=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    # -----------------------------
    # CREATE
    # -----------------------------
    @staticmethod
    def create(name, phone=None, email=None):
        query = """
            INSERT INTO customers (name, phone, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """
        created_at = datetime.now().isoformat()
        updated_at = datetime.now().isoformat()
        
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
            return None 
        
        # Acceso por nombre de columna
        r = rows[0]
        return Customer(
            id=r['id'],
            name=r['name'],
            phone=r['phone'],
            email=r['email'],
            created_at=r['created_at'],
            updated_at=r['updated_at']
        )

    # -----------------------------
    # GET ALL
    # -----------------------------
    @staticmethod
    def all():
        rows = db.fetch("SELECT id, name, phone, email, created_at, updated_at FROM customers")

        return [
            {
                # Acceso por nombre de columna
                "id": r['id'],
                "name": r['name'],
                "phone": r['phone'],
                "email": r['email'],
                "created_at": r['created_at'],
                "updated_at": r['updated_at']
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
        
        db.execute(query, (self.name, self.phone, self.email, self.updated_at, self.id))

    # -----------------------------
    # DELETE
    # -----------------------------
    def delete(self):
        if self.id is None:
            raise ValueError("Customer must have an ID to delete.")

        db.execute("DELETE FROM customers WHERE id=?", (self.id,))