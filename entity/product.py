import os.path
from csv import reader


class Product:
    """Product Class"""

    def __init__(self, product_id):
        product_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../table/product_db.csv"))
        product_entry = None
        with open(product_db_path, 'r', newline='') as file_object:
            reader_object = reader(file_object, delimiter=',')
            for entry in reader_object:
                if entry[0] == product_id:
                    product_entry = entry
            file_object.close()

        if not product_entry:
            raise ValueError
            
        self.name = product_entry[1]
        self.price = int(product_entry[2])
