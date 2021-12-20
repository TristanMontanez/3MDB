from base_controller import BaseControllerClass

import os.path
from typing import List

DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../table'))
DATABASE_PATH = os.path.join(DATABASE_PATH, 'customer_db.csv')


class CustomerController(BaseControllerClass):
    """Customer Controller Class"""

    def __init__(self):
        super().__init__(entry_db=DATABASE_PATH)

    def get_all_customer_names(self, alphabetical: bool = True):
        """
        Gets all customer names from DB
        :param alphabetical: if False returns by order in DB
        :return: List of names
        """
        names = self.get_all_by_column(column=1,
                                       alphabetical=alphabetical)
        return names

    def get_customer_name_by_id(self, customer_id: str) -> List:
        """
        Returns name by customer_id
        :param customer_id: Customer ID
        :return: Customer Name
        """
        customer = self.search_db({'customer_id': customer_id})
        if customer:
            return customer[0][1]

        return []

    def get_customer_id_by_name(self, name: str, department: str = None) -> List:
        """
        Returns customer_id by name
        :param name: Customer Name
        :param department: Department
        :return: Customer ID
        """
        query = {'name': name}
        if department:
            query['section'] = department

        customer = self.search_db({'name': name})
        if customer and len(customer) == 1:
            return customer[0][0]

        return []
