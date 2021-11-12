import uuid
import os.path
import datetime

from csv import writer, reader
from entity.product import Product

DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../table'))
PRODUCT_DB_PATH = os.path.join(DATABASE_PATH, 'product_db.csv')


class Order:
    """Order Class"""

    def __init__(self, customer_id: str, product_id: str, quantity: int):
        self.quantity = quantity
        self.order_id = datetime.date.today().strftime('%m_%d_%Y_') + str(uuid.uuid4())
        self.customer_id = customer_id
        self.total = 0

        if type(product_id) is int:
            product_id = str(product_id)

        price = self.search_product_price(product_id)
        if price:
            self.total = int(price) * int(quantity)

    @staticmethod
    def search_product_price(product_id):
        """returns price of given product"""
        order_db = reader(open(PRODUCT_DB_PATH, 'r'), delimiter=',')
        for row in order_db:
            if product_id == row[0]:
                return row[2]
        return None
