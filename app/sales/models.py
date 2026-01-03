from app.core.extensions import db
from app.models.base import BaseModel
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import event

class CustomerCategory(BaseModel):
    __tablename__ = 'customer_categories'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    payment_terms_days = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<CustomerCategory {self.name}>'

class Customer(BaseModel):
    __tablename__ = 'customers'
    
    # Basic Information
    customer_code = db.Column(db.String(20), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    title = db.Column(db.String(50))
    
    # Contact Details
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Address Information
    billing_address = db.Column(db.Text)
    shipping_address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Business Information
    tax_id = db.Column(db.String(50))
    registration_number = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    customer_category_id = db.Column(db.Integer, db.ForeignKey('customer_categories.id'))
    
    # Financial Information
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    payment_terms = db.Column(db.String(50), default='Net 30')
    currency = db.Column(db.String(3), default='USD')
    
    # Status and Settings
    status = db.Column(db.String(20), default='active')
    is_vip = db.Column(db.Boolean, default=False)
    assigned_salesperson_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    category = db.relationship('CustomerCategory', backref='customers')
    salesperson = db.relationship('User', backref='assigned_customers')

    @property
    def display_name(self):
        return f"{self.company_name} ({self.customer_code})"
    
    @property
    def available_credit(self):
        return self.credit_limit - self.current_balance

    def __repr__(self):
        return f'<Customer {self.customer_code}: {self.company_name}>'

class SalesOrder(BaseModel):
    __tablename__ = 'sales_orders'
    
    # Order Information
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    salesperson_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Dates
    order_date = db.Column(db.Date, nullable=False, default=date.today)
    required_date = db.Column(db.Date)
    promised_date = db.Column(db.Date)
    shipped_date = db.Column(db.Date)
    
    # Financial Information
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Status and Processing
    status = db.Column(db.String(20), default='draft')  # draft, pending, confirmed, processing, shipped, delivered, cancelled
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Shipping Information
    shipping_method = db.Column(db.String(50))
    shipping_address = db.Column(db.Text)
    tracking_number = db.Column(db.String(100))
    
    # Payment Information
    payment_terms = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid, overdue
    
    # Notes and References
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    reference_number = db.Column(db.String(50))
    
    # Relationships
    customer = db.relationship('Customer', backref='orders')
    salesperson = db.relationship('User', backref='sales_orders')

    def calculate_totals(self):
        """Calculate order totals from line items"""
        self.subtotal = sum(item.line_total for item in self.items)
        self.tax_amount = self.subtotal * 0.085  # 8.5% tax rate
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount

    def __repr__(self):
        return f'<SalesOrder {self.order_number}>'

class SalesOrderItem(BaseModel):
    __tablename__ = 'sales_order_items'
    
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    line_total = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Fulfillment
    quantity_shipped = db.Column(db.Integer, default=0)
    quantity_backordered = db.Column(db.Integer, default=0)
    
    # Relationships
    order = db.relationship('SalesOrder', backref='items')
    product = db.relationship('Product', backref='order_items')

    def calculate_line_total(self):
        """Calculate line total with discounts"""
        discounted_price = self.unit_price - self.discount_amount
        if self.discount_percentage > 0:
            discounted_price = self.unit_price * (1 - self.discount_percentage / 100)
        self.line_total = self.quantity * discounted_price

    def __repr__(self):
        return f'<SalesOrderItem Order:{self.order_id} Product:{self.product_id}>'

class Quote(BaseModel):
    __tablename__ = 'quotes'
    
    # Quote Information
    quote_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    salesperson_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Dates
    quote_date = db.Column(db.Date, nullable=False, default=date.today)
    valid_until = db.Column(db.Date, nullable=False)
    
    # Financial Information
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, accepted, rejected, expired
    
    # Notes
    notes = db.Column(db.Text)
    terms_conditions = db.Column(db.Text)
    
    # Relationships
    customer = db.relationship('Customer', backref='quotes')
    salesperson = db.relationship('User', backref='quotes')

    @property
    def is_expired(self):
        return date.today() > self.valid_until

    def __repr__(self):
        return f'<Quote {self.quote_number}>'

class QuoteItem(BaseModel):
    __tablename__ = 'quote_items'
    
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    line_total = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Relationships
    quote = db.relationship('Quote', backref='items')
    product = db.relationship('Product', backref='quote_items')

    def __repr__(self):
        return f'<QuoteItem Quote:{self.quote_id} Product:{self.product_id}>'

# Auto-generate codes for new records
@event.listens_for(Customer, 'before_insert')
def generate_customer_code(mapper, connection, target):
    if not target.customer_code:
        # Get the last customer number
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(customer_code, 5) AS INTEGER)) FROM customers WHERE customer_code LIKE 'CUST%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.customer_code = f"CUST{next_num:06d}"

@event.listens_for(SalesOrder, 'before_insert')
def generate_order_number(mapper, connection, target):
    if not target.order_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(order_number, 4) AS INTEGER)) FROM sales_orders WHERE order_number LIKE 'ORD%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.order_number = f"ORD{next_num:06d}"

@event.listens_for(Quote, 'before_insert')
def generate_quote_number(mapper, connection, target):
    if not target.quote_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(quote_number, 4) AS INTEGER)) FROM quotes WHERE quote_number LIKE 'QUO%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.quote_number = f"QUO{next_num:06d}"