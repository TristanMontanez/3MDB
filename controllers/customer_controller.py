from base_controller import BaseControllerClass

import os.path
from typing import Dict

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

    def search_customer_by_query(self, query: Dict) -> Dict:
        """
        Returns Customer DB item
        :param query: Dictionary with format {search_parameter: term}
        :return: Customer Dictionary with given query
        """
        pass
