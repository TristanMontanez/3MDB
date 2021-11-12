import uuid
import datetime

class Customer:
    """Customer Class"""

    def __init__(self, name: str,
                 employed_date=datetime.date(1, 2, 3),
                 department=''):
        self.name = name
        self.customer_id = uuid.uuid4()
        self.employed_date = employed_date

        departments = [
            'ICING',
            'ICING (DAILY)',
            'QC',
            'PACKING',
        ]

        if department in departments:
            self.department = department
