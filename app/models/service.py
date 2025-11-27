from app.database import Database

db = Database()

class Service:

    @staticmethod
    def create(name, price):
        query = """
        INSERT INTO services (name, price)
        VALUES (?, ?);
        """
        db.execute(query, (name, price))

    @staticmethod
    def get_all():
        query = "SELECT * FROM services;"
        return db.fetch(query)

    @staticmethod
    def get_by_id(service_id):
        query = "SELECT * FROM services WHERE id = ?;"
        return db.fetch(query, (service_id,))

    @staticmethod
    def update(service_id, name, price):
        query = """
        UPDATE services
        SET name = ?, price = ?
        WHERE id = ?;
        """
        db.execute(query, (name, price, service_id))

    @staticmethod
    def delete(service_id):
        query = "DELETE FROM services WHERE id = ?;"
        db.execute(query, (service_id,))
