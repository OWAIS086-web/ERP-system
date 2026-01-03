from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.inventory import bp

@bp.route('/products')
@login_required
def products():
    return render_template('inventory/products.html')

@bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        # Handle product creation logic here
        flash('Product created successfully!', 'success')
        return redirect(url_for('inventory.products'))
    
    categories = []  # TODO: Get from database
    brands = []      # TODO: Get from database
    units = []       # TODO: Get from database
    return render_template('inventory/add_product.html', 
                         categories=categories, 
                         brands=brands, 
                         units=units)

@bp.route('/products/<int:id>')
@login_required
def product_detail(id):
    # TODO: Get product from database
    product = None
    warehouses = []  # TODO: Get from database
    return render_template('inventory/product_detail.html', 
                         product=product, 
                         warehouses=warehouses)

@bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if request.method == 'POST':
        # Handle product update logic here
        flash('Product updated successfully!', 'success')
        return redirect(url_for('inventory.product_detail', id=id))
    
    # TODO: Get product from database
    product = None
    categories = []  # TODO: Get from database
    brands = []      # TODO: Get from database
    units = []       # TODO: Get from database
    return render_template('inventory/edit_product.html', 
                         product=product,
                         categories=categories, 
                         brands=brands, 
                         units=units)

@bp.route('/categories')
@login_required
def categories():
    return render_template('inventory/categories.html')

@bp.route('/categories/<int:id>')
@login_required
def category_detail(id):
    # TODO: Get category from database
    category = None
    return render_template('inventory/category_detail.html', category=category)

@bp.route('/brands')
@login_required
def brands():
    return render_template('inventory/brands.html')

@bp.route('/brands/<int:id>')
@login_required
def brand_detail(id):
    # TODO: Get brand from database
    brand = None
    return render_template('inventory/brand_detail.html', brand=brand)

@bp.route('/stock')
@login_required
def stock():
    return render_template('inventory/stock.html')

@bp.route('/stock/adjustment', methods=['GET', 'POST'])
@login_required
def stock_adjustment():
    if request.method == 'POST':
        # Handle stock adjustment logic here
        flash('Stock adjustment recorded successfully!', 'success')
        return redirect(url_for('inventory.stock'))
    
    products = []    # TODO: Get from database
    warehouses = []  # TODO: Get from database
    return render_template('inventory/stock_adjustment.html', 
                         products=products, 
                         warehouses=warehouses)

@bp.route('/stock/movements')
@login_required
def stock_movements():
    movements = []   # TODO: Get from database
    products = []    # TODO: Get from database
    warehouses = []  # TODO: Get from database
    return render_template('inventory/stock_movements.html', 
                         movements=movements,
                         products=products, 
                         warehouses=warehouses)