from flask import Flask, render_template, request, redirect, url_for, session
import main_library as ml

app = Flask(__name__)
app.secret_key = 'migokian'

CUSTOMER_NAME_LIST = ml.get_all_customer_names_alphabetically()
PRODUCT_LIST = ml.get_all_product_names()
DEDUCTIBLE_LIST = ml.get_all_deductible_names()


@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'POST' and request.form.get('go_to_order_history'):
        return redirect(url_for("home_order_history"))
    elif request.method == 'POST' and request.form.get('go_to_create_order'):
        return redirect(url_for("create_order"))
    elif request.method == 'POST' and request.form.get('go_to_create_other'):
        return redirect(url_for("create_other"))
    elif request.method == 'POST' and request.form.get('create_deduction_file'):
        ml.create_excel_file()
        return redirect(url_for("redirect_to_home"))
    else:
        return render_template('home.html')


@app.route("/create_order", methods=['POST', 'GET'])
def create_order():
    if request.method == 'POST':
        current_order = {
            'customer_id': None,
            'product_id_list': [],
            'quantity_list': [],
        }

        customer_id = ml.get_customer_id_by_name(request.form.get('customer_name'))
        if not customer_id:
            return "Order Creation Failed: Customer Name not found in DB"

        current_order['customer_id'] = customer_id

        for i in range(0, 12):
            product_name = request.form.get('product_'+str(i))
            quantity = request.form.get('quantity_'+str(i))
            product_id = ml.get_product_id_by_name(product_name=product_name)
            if product_name and quantity:
                current_order['product_id_list'].append(product_id)
                current_order['quantity_list'].append(quantity)

        session['order'] = current_order
        product_ids = session['order'].get('product_id_list')
        quantities = session['order'].get('quantity_list')
        order_id = ml.create_multiple_orders(product_id_list=product_ids,
                                             quantity_list=quantities,
                                             customer_id=session['order'].get('customer_id'))
        session['order_id'] = order_id
        return redirect(url_for("created_order"))
    else:
        return render_template('create_order.html', name_list=CUSTOMER_NAME_LIST, products=PRODUCT_LIST)


@app.route("/create_other", methods=['POST', 'GET'])
def create_other():
    if request.method == 'POST':
        # current_deductible = {
        #     'customer_id': None,
        #     'deductible_id_list': [],
        #     'quantity_list': [],
        #     'monthly_list': [],
        # }

        customer_id = ml.get_customer_id_by_name(request.form.get('customer_name'))
        if not customer_id:
            return "Order Creation Failed: Customer Name not found in DB"

        session['other'] = {'customer_id': customer_id}
        deductible_list = []
        for i in range(0, 12):
            deductible_name = request.form.get('deductible_'+str(i))
            price = request.form.get('price_'+str(i))
            monthly = request.form.get('monthly_'+str(i))
            deductible_id = ml.get_deductible_id_by_name(deductible_name=deductible_name)
            if deductible_id and price and monthly:
                deductible = [price, deductible_id, monthly]
                deductible_list.append(deductible)
                ml.create_multiple_deductibles(deductible_list=deductible_list,
                                               customer_id=customer_id)

        return redirect(url_for("created_other"))
    else:
        return render_template('create_other.html', name_list=CUSTOMER_NAME_LIST, deductibles=DEDUCTIBLE_LIST)


@app.route("/create_order/redirect", methods=['POST', 'GET'])
def created_order():
    if request.method == 'POST':
        return redirect(url_for("home"))
    else:
        customer_name = ml.get_customer_name_by_id(customer_id=session['order'].get('customer_id'))
        product_ids = session['order'].get('product_id_list')
        quantities = session['order'].get('quantity_list')
        orders = []
        total = 0
        for i in range(0,len(product_ids)):
            product_data = ml.get_product_data_by_id(product_id=product_ids[i])
            amount = int(product_data[1]) * int(quantities[i])
            total += amount
            orders.append([product_data[0], product_data[1], quantities[i], amount])

        return render_template('created_order.html',
                               customer_name=customer_name,
                               orders=orders,
                               total=total,
                               order_id=session['order_id'])


@app.route("/create_other/redirect", methods=['POST', 'GET'])
def created_other():
    if request.method == 'POST':
        return redirect(url_for("home"))
    else:
        customer_name = ml.get_customer_name_by_id(customer_id=session['other'].get('customer_id'))
        deductible_data = ml.get_all_deductible_data_by_customer_id(customer_id=session['other'].get('customer_id'))
        return render_template('created_other.html',
                               customer_name=customer_name,
                               data=deductible_data)


@app.route("/order_history/", methods=['POST', 'GET'])
def home_order_history():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        return redirect(url_for("customer_order_history", customer_name=customer_name))
    else:
        return render_template('home_order_history.html', name_list=CUSTOMER_NAME_LIST)


@app.route("/order_history/<customer_name>", methods=['POST', 'GET'])
def customer_order_history(customer_name):
    if request.method == 'POST':
        return redirect(url_for("home"))

    customer_id = ml.get_customer_id_by_name(customer_name=customer_name)
    orders = ml.get_all_orders_by_customer_id(customer_id=customer_id)
    total = ml.get_balance_by_customer_id(customer_id=customer_id)[1]
    other_deductibles = ml.get_all_deductible_data_by_customer_id(customer_id=customer_id)
    return render_template('customer_order_history.html',
                           customer_name=customer_name,
                           orders=orders,
                           total=total,
                           other_deductibles=other_deductibles)


@app.route("/redirect", methods=['POST', 'GET'])
def redirect_to_home():
    if request.method == 'POST':
        return redirect(url_for("home"))
    return render_template('redirect_to_home.html')


if __name__ == '__main__':
    app.run(debug=True)
