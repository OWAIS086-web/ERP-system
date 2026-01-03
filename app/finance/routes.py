from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.finance import bp

@bp.route('/invoices')
@login_required
def invoices():
    return render_template('finance/invoices.html')

@bp.route('/invoices/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    if request.method == 'POST':
        # Handle invoice creation logic here
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('finance.invoices'))
    
    customers = []  # TODO: Get from database
    products = []   # TODO: Get from database
    return render_template('finance/create_invoice.html', 
                         customers=customers, 
                         products=products)

@bp.route('/invoices/<int:id>')
@login_required
def invoice_detail(id):
    # TODO: Get invoice from database
    invoice = None
    return render_template('finance/invoice_detail.html', invoice=invoice)

@bp.route('/invoices/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_invoice(id):
    if request.method == 'POST':
        # Handle invoice update logic here
        flash('Invoice updated successfully!', 'success')
        return redirect(url_for('finance.invoice_detail', id=id))
    
    # TODO: Get invoice from database
    invoice = None
    customers = []  # TODO: Get from database
    products = []   # TODO: Get from database
    return render_template('finance/edit_invoice.html', 
                         invoice=invoice,
                         customers=customers, 
                         products=products)

@bp.route('/payments')
@login_required
def payments():
    return render_template('finance/payments.html')

@bp.route('/payments/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    if request.method == 'POST':
        # Handle payment creation logic here
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('finance.payments'))
    
    invoices = []   # TODO: Get from database
    customers = []  # TODO: Get from database
    return render_template('finance/add_payment.html', 
                         invoices=invoices, 
                         customers=customers)

@bp.route('/payments/<int:id>')
@login_required
def payment_detail(id):
    # TODO: Get payment from database
    payment = None
    return render_template('finance/payment_detail.html', payment=payment)

@bp.route('/expenses')
@login_required
def expenses():
    return render_template('finance/expenses.html')

@bp.route('/expenses/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        # Handle expense creation logic here
        flash('Expense recorded successfully!', 'success')
        return redirect(url_for('finance.expenses'))
    
    categories = []  # TODO: Get from database
    employees = []   # TODO: Get from database
    return render_template('finance/add_expense.html', 
                         categories=categories, 
                         employees=employees)

@bp.route('/expenses/<int:id>')
@login_required
def expense_detail(id):
    # TODO: Get expense from database
    expense = None
    return render_template('finance/expense_detail.html', expense=expense)