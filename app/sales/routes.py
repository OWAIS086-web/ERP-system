from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.sales import bp

@bp.route('/customers')
@login_required
def customers():
    return render_template('sales/customers.html')

@bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        # Handle customer creation logic here
        flash('Customer created successfully!', 'success')
        return redirect(url_for('sales.customers'))
    
    categories = []  # TODO: Get from database
    return render_template('sales/add_customer.html', categories=categories)

@bp.route('/customers/<int:id>')
@login_required
def customer_detail(id):
    # TODO: Get customer from database
    customer = None
    return render_template('sales/customer_detail.html', customer=customer)

@bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    if request.method == 'POST':
        # Handle customer update logic here
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('sales.customer_detail', id=id))
    
    # TODO: Get customer from database
    customer = None
    categories = []  # TODO: Get from database
    return render_template('sales/edit_customer.html', customer=customer, categories=categories)

@bp.route('/orders')
@login_required
def orders():
    return render_template('sales/orders.html')

@bp.route('/orders/add', methods=['GET', 'POST'])
@login_required
def add_order():
    if request.method == 'POST':
        # Handle order creation logic here
        flash('Order created successfully!', 'success')
        return redirect(url_for('sales.orders'))
    
    customers = []  # TODO: Get from database
    products = []   # TODO: Get from database
    return render_template('sales/add_order.html', customers=customers, products=products)

@bp.route('/orders/<int:id>')
@login_required
def order_detail(id):
    # TODO: Get order from database
    order = None
    return render_template('sales/order_detail.html', order=order)

@bp.route('/orders/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(id):
    if request.method == 'POST':
        # Handle order update logic here
        flash('Order updated successfully!', 'success')
        return redirect(url_for('sales.order_detail', id=id))
    
    # TODO: Get order from database
    order = None
    customers = []  # TODO: Get from database
    products = []   # TODO: Get from database
    return render_template('sales/edit_order.html', order=order, customers=customers, products=products)

@bp.route('/quotes')
@login_required
def quotes():
    return render_template('sales/quotes.html')

@bp.route('/quotes/add', methods=['GET', 'POST'])
@login_required
def add_quote():
    if request.method == 'POST':
        # Handle quote creation logic here
        flash('Quote created successfully!', 'success')
        return redirect(url_for('sales.quotes'))
    
    customers = []  # TODO: Get from database
    products = []   # TODO: Get from database
    return render_template('sales/add_quote.html', customers=customers, products=products)

@bp.route('/quotes/<int:id>')
@login_required
def quote_detail(id):
    # TODO: Get quote from database
    quote = None
    return render_template('sales/quote_detail.html', quote=quote)