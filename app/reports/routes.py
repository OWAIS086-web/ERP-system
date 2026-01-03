from flask import render_template, request
from flask_login import login_required
from app.reports import bp
from datetime import datetime, date, timedelta

@bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')

@bp.route('/sales-summary')
@login_required
def sales_summary():
    # Mock data for now - TODO: Replace with actual database queries
    customers = []  # TODO: Get from database
    
    # Mock metrics
    metrics = {
        'total_sales': 0,
        'sales_growth': 0,
        'total_orders': 0,
        'orders_growth': 0,
        'average_order_value': 0,
        'aov_growth': 0,
        'unique_customers': 0,
        'customer_growth': 0,
        'conversion_rate': 0,
        'repeat_customer_rate': 0,
        'revenue_per_customer': 0,
        'avg_days_to_close': 0,
        'current_period_sales': 0,
        'previous_period_sales': 0
    }
    
    # Mock chart data
    sales_trend_labels = []
    sales_trend_data = []
    category_labels = []
    category_data = []
    
    top_products = []  # TODO: Get from database
    top_customers = []  # TODO: Get from database
    
    return render_template('reports/sales_summary.html',
                         customers=customers,
                         metrics=metrics,
                         sales_trend_labels=sales_trend_labels,
                         sales_trend_data=sales_trend_data,
                         category_labels=category_labels,
                         category_data=category_data,
                         top_products=top_products,
                         top_customers=top_customers)

@bp.route('/inventory-report')
@login_required
def inventory_report():
    # Mock data for now - TODO: Replace with actual database queries
    warehouses = []   # TODO: Get from database
    categories = []   # TODO: Get from database
    products = []     # TODO: Get from database
    
    # Mock metrics
    metrics = {
        'total_products': 0,
        'active_products': 0,
        'total_inventory_value': 0,
        'low_stock_items': 0,
        'out_of_stock_items': 0,
        'in_stock_items': 0,
        'overstock_items': 0
    }
    
    low_stock_products = []    # TODO: Get from database
    category_breakdown = []    # TODO: Get from database
    warehouse_breakdown = []   # TODO: Get from database
    
    return render_template('reports/inventory_report.html',
                         warehouses=warehouses,
                         categories=categories,
                         products=products,
                         metrics=metrics,
                         low_stock_products=low_stock_products,
                         category_breakdown=category_breakdown,
                         warehouse_breakdown=warehouse_breakdown)