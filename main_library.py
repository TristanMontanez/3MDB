import csv
import datetime
import os.path
import xlsxwriter

from typing import List
from csv import writer, reader
from shutil import copyfile
from operator import itemgetter

from entity.order import Order

DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'table'))
OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output'))
BACKUP_PATH = os.path.join(OUTPUT_PATH, 'backup')
CUSTOMER_DB_PATH = os.path.join(DATABASE_PATH, 'customer_db.csv')
ORDER_DB_PATH = os.path.join(DATABASE_PATH, 'order_db.csv')
DEDUCTIBLE_DB_PATH = os.path.join(DATABASE_PATH, 'deductible_db.csv')
DEDUCTIBLE_ID_DB_PATH = os.path.join(DATABASE_PATH, 'deductible_id_db.csv')
PRODUCT_DB_PATH = os.path.join(DATABASE_PATH, 'product_db.csv')


# =========================================== WRITES =========================================== #
def create_multiple_orders(product_id_list: List[str],
                           quantity_list: List[int],
                           customer_id: str):
    """creates multiple order entities and uploads to database"""
    if len(product_id_list) != len(quantity_list):
        raise ValueError('Product ID count != Quantity count')

    i = 0
    entry_items = []
    order = None
    while i < len(product_id_list):
        order = Order(customer_id=customer_id,
                      product_id=product_id_list[i],
                      quantity=quantity_list[i])
        entry_items.append([order.order_id, customer_id, order.total, product_id_list[i], quantity_list[i]])
        i += 1

    if entry_items:
        __upload_multiple_to_db(entry_items=entry_items,
                                upload_path=ORDER_DB_PATH)

    return order.order_id


def create_multiple_deductibles(deductible_list: List,
                                customer_id: str):
    """creates multiple order entities and uploads to database"""
    date = datetime.date.today().strftime('%b %d, %Y')
    entry_items = []
    for price, deductible_id, monthly in deductible_list:
        entry_items.append([customer_id, price, deductible_id, monthly, 0, date])

    if entry_items:
        __upload_multiple_to_db(entry_items=entry_items,
                                upload_path=DEDUCTIBLE_DB_PATH)


def create_excel_file():
    """creates excel file in output directory"""
    file_path = os.path.join(OUTPUT_PATH, 'DEDUCTION_' + datetime.date.today().strftime('%b_%d_%Y') + '.xlsx')

    i = 2
    while os.path.exists(file_path):
        file_path = os.path.join(OUTPUT_PATH, 'DEDUCTION_' + datetime.date.today().strftime('%b_%d_%Y') + f'_{i}.xlsx')
        print(file_path)
        i += 1

    file_path = __does_file_already_exist(file_path)

    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()
    cell_header = workbook.add_format()
    cell_header.set_bold()
    cell_header.set_align('center')

    cell_number = workbook.add_format()
    cell_number.set_align('right')
    cell_number.set_border()

    cell_currency = workbook.add_format()
    cell_currency.set_align('right')
    cell_currency.set_border()
    cell_currency.set_num_format('#,##0.00')

    cell_format = workbook.add_format()
    cell_format.set_border()

    worksheet.set_column('A:A', 3)
    worksheet.set_column('B:B', 35)
    worksheet.set_column('C:E', 13)

    departments = [
        'ICING',
        'ICING (DAILY)',
        'QC',
        'PACKING',
    ]

    row = 1
    count = 1
    for department in departments:

        worksheet.write(row, 1, department, cell_header)
        worksheet.write(row, 2, 'GROCERY', cell_header)
        worksheet.write(row, 3, 'OTHER', cell_header)
        worksheet.write(row, 4, 'TOTAL', cell_header)
        customer_ids = __search_customer_db_per_department(department=department)
        row += 1
        for customer_id, name in customer_ids:
            balance = get_balance_by_customer_id(customer_id)
            if balance[0]:
                worksheet.write(row, 0, count, cell_number)
                worksheet.write(row, 1, name, cell_format)
                worksheet.write(row, 2, balance[1], cell_currency)
                worksheet.write(row, 3, balance[2], cell_currency)
                worksheet.write(row, 4, balance[0], cell_currency)
                row += 1
                count += 1

        row += 1

    print('Excel File Updated')
    workbook.close()


def update_order_and_deductible_db():
    """
    Creates a backup of order_db.csv and deductible_db.csv then updates the values
    Clears grocery orders, subtracts monthly from deductibles
    """
    date = datetime.date.today().strftime('%b_%Y')
    copyfile(ORDER_DB_PATH, os.path.join(BACKUP_PATH, f'order_db_{date}.csv'))
    copyfile(DEDUCTIBLE_DB_PATH, os.path.join(BACKUP_PATH, f'deductible_db_{date}.csv'))

    with open(ORDER_DB_PATH, 'w', newline='') as order_file:
        order_file_writer = csv.writer(order_file)
        order_file_writer.writerow(['order_id', 'customer_id', 'total', 'product_id', 'quantity'])
        order_file.close()

    new_deductible_db_list = []
    deductible_db = reader(open(DEDUCTIBLE_DB_PATH, 'r'), delimiter=',')
    for row in deductible_db:
        paid = row[4] + row[3]
        if paid <= row[1]:
            new_deductible_db_list.append([
                row[0],                         # customer_id
                row[1],                         # price
                row[2],                         # deductible_id
                row[3],                         # monthly
                paid,                           # paid
                row[5]                          # date purchased
            ])

    with open(DEDUCTIBLE_DB_PATH, 'w', newline='') as order_file:
        order_file_writer = csv.writer(order_file)
        order_file_writer.writerow(['customer_id', 'price', 'deductible_id', 'monthly', 'paid', 'date_purchased'])
        order_file.close()


def register_customer(customer_name: str,
                      department: str):
    """Registers customer to customer DB"""
    customer_db = reader(open(CUSTOMER_DB_PATH, 'r'), delimiter=',')
    i = 0
    if department not in ['ICING', 'ICING (DAILY)', 'QC', 'PACKING']:
        raise ValueError

    for _ in customer_db:
        i += 1

    customer_id = f'Customer_{str(i).zfill(4)}'
    __upload_multiple_to_db(entry_items=[[customer_id, customer_name.replace(' ', '_'), department]],
                            upload_path=CUSTOMER_DB_PATH)
# ============================================================================================== #


# ========================================== CUSTOMER ========================================== #
def get_all_customer_names_alphabetically():
    """returns an alphabetical order of all customer names"""
    customer_db = reader(open(CUSTOMER_DB_PATH, 'r'), delimiter=',')
    customers = []
    for row in customer_db:
        customers.append(row[1])
    customers.pop(0)
    return sorted(customers)


def get_customer_name_by_id(customer_id: str):
    """searches customer database and returns customer name with corresponding id"""
    customer_db = reader(open(CUSTOMER_DB_PATH, 'r'), delimiter=',')
    for row in customer_db:
        if customer_id == row[0]:
            return row[1]
    return None


def get_customer_id_by_name(customer_name: str):
    """searches customer database and returns customer id with corresponding name"""
    customer_db = reader(open(CUSTOMER_DB_PATH, 'r'), delimiter=',')
    for row in customer_db:
        if customer_name == row[1]:
            return row[0]
    return None
# ============================================================================================== #


# ========================================== PRODUCT =========================================== #
def get_all_product_names():
    """returns an alphabetical order of all products"""
    product_db = reader(open(PRODUCT_DB_PATH, 'r'), delimiter=',')
    products = []
    for row in product_db:
        products.append(row[1])
    products.pop(0)
    return sorted(products)


def get_product_id_by_name(product_name: str):
    """searches product database and returns product id with corresponding name"""
    product_db = reader(open(PRODUCT_DB_PATH, 'r'), delimiter=',')
    for row in product_db:
        if product_name == row[1]:
            return row[0]
    return None


def get_product_data_by_id(product_id: str):
    """searches product database and returns product name, price with corresponding id"""
    product_db = reader(open(PRODUCT_DB_PATH, 'r'), delimiter=',')
    for row in product_db:
        if product_id == row[0]:
            return [row[1], row[2]]
    return None
# ============================================================================================== #


# ======================================= DEDUCTIBLES ========================================== #
def get_all_deductible_names():
    """returns an alphabetical order of all deductibles"""
    deductible_db = reader(open(DEDUCTIBLE_ID_DB_PATH, 'r'), delimiter=',')
    deductibles = []
    for row in deductible_db:
        deductibles.append(row[1])
    deductibles.pop(0)
    return sorted(deductibles)


def get_deductible_id_by_name(deductible_name: str):
    """searches deductible database and returns product id with corresponding name"""
    deductible_db = reader(open(DEDUCTIBLE_ID_DB_PATH, 'r'), delimiter=',')
    for row in deductible_db:
        if deductible_name == row[1]:
            return row[0]
    return None


def get_deductible_data_by_id(deductible_id: str):
    """searches deductible database and returns product name, price with corresponding id"""
    deductible_db = reader(open(DEDUCTIBLE_ID_DB_PATH, 'r'), delimiter=',')
    for row in deductible_db:
        if deductible_id == row[0]:
            return [row[1], row[2]]
    return None


def get_all_orders_by_customer_id(customer_id: str):
    """get all orders by customer"""
    order_db = reader(open(ORDER_DB_PATH, 'r'), delimiter=',')
    orders = []
    for row in order_db:
        if customer_id == row[1]:
            product_data = get_product_data_by_id(product_id=row[3])
            if product_data:
                orders.append([product_data[0], product_data[1], row[4], row[2]])
    return orders


def get_all_deductible_data_by_customer_id(customer_id: str):
    """returns all deductibles by customer id"""
    deductible_db = reader(open(DEDUCTIBLE_DB_PATH, 'r'), delimiter=',')
    deductible_data = []
    for row in deductible_db:
        if customer_id == row[0]:
            deductible = get_deductible_data_by_id(deductible_id=row[2])
            deductible_data.append([
                deductible[0],
                row[3],
                row[4],
                deductible[1],
                row[5]
            ])
    return deductible_data
# ============================================================================================== #


def get_balance_by_customer_id(customer_id: str):
    """searches order database and returns balance of customer"""
    order_db = reader(open(ORDER_DB_PATH, 'r'), delimiter=',')
    deductible_db = reader(open(DEDUCTIBLE_DB_PATH, 'r'), delimiter=',')

    grocery_bal = 0
    for row in order_db:
        if customer_id == row[1]:
            grocery_bal += int(row[2])

    deductible_bal = 0
    for row in deductible_db:
        if customer_id == row[0]:
            deductible_bal += int(row[3])

    return [grocery_bal + deductible_bal, grocery_bal, deductible_bal]


def __does_file_already_exist(file_path: str):
    """changes file_path name if filename already exists"""
    if os.path.exists(file_path):
        i = 2
        new_file_path = file_path + '_' + str(i)
        while os.path.exists(new_file_path):
            i += 1
            new_file_path = file_path + '_' + str(i)
        file_path = new_file_path
    return file_path


def __upload_multiple_to_db(entry_items: List[List[str]],
                            upload_path: str):
    """uploads multiple items to respective DB"""
    with open(upload_path, 'a', newline='') as file_object:
        writer_object = writer(file_object)
        for entry in entry_items:
            writer_object.writerow(entry)
        file_object.close()


def __search_customer_db_per_department(department: str):
    """searches customer database and returns all customer ids with corresponding department"""
    customer_db = reader(open(CUSTOMER_DB_PATH, 'r'), delimiter=',')

    items = []
    for row in customer_db:
        if department == row[2]:
            items.append([row[0], row[1].replace('_', ' ').upper()])

    return sorted(items, key=itemgetter(1))
