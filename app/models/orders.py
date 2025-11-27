from app.database import Database

db = Database()

class Order:

    @staticmethod
    def create(customer_id, service_id, date, status="pending"):
        query = """
        INSERT INTO orders (customer_id, service_id, date, status)
        VALUES (?, ?, ?, ?);
        """
        db.execute(query, (customer_id, service_id, date, status))

    @staticmethod
    def get_all():
        query = "SELECT * FROM orders;"
        return db.fetch(query)

    @staticmethod
    def get_by_id(order_id):
        query = "SELECT * FROM orders WHERE id = ?;"
        return db.fetch(query, (order_id,))

    @staticmethod
    def update_status(order_id, new_status):
        query = "UPDATE orders SET status = ? WHERE id = ?;"
        db.execute(query, (new_status, order_id))

    @staticmethod
    def delete(order_id):
        query = "DELETE FROM orders WHERE id = ?;"
        db.execute(query, (order_id,))
