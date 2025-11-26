from app.database import Database

db = Database()

class Customer:

    @staticmethod
    def create(name, phone, email):
        query = """
        INSERT INTO customers (name, phone, email)
        VALUES (?, ?, ?);
        """
        db.execute(query, (name, phone, email))

    @staticmethod
    def get_all():
        query = "SELECT * FROM customers;"
        return db.fetch(query)

    @staticmethod
    def get_by_id(customer_id):
        query = "SELECT * FROM customers WHERE id = ?;"
        return db.fetch(query, (customer_id,))

    @staticmethod
    def delete(customer_id):
        query = "DELETE FROM customers WHERE id = ?;"
        db.execute(query, (customer_id,))
