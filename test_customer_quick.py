from app.models.customers import Customer

Customer.create("Ray sosa", "442143", "ray@gmail.com")
print(Customer.get_all())
