from app.core.extensions import db
from app.models.base import BaseModel
from datetime import datetime
from decimal import Decimal
from sqlalchemy import event

class ProductCategory(BaseModel):
    __tablename__ = 'product_categories'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    code = db.Column(db.String(20), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Self-referential relationship for hierarchical categories
    parent = db.relationship('ProductCategory', remote_side='ProductCategory.id', backref='subcategories')

    @property
    def full_path(self):
        """Get full category path"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    def __repr__(self):
        return f'<ProductCategory {self.name}>'

class Brand(BaseModel):
    __tablename__ = 'brands'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(200))
    website = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Brand {self.name}>'

class UnitOfMeasure(BaseModel):
    __tablename__ = 'units_of_measure'
    
    name = db.Column(db.String(50), nullable=False)
    abbreviation = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(20))  # weight, volume, length, quantity
    base_unit_conversion = db.Column(db.Numeric(10, 4), default=1)

    def __repr__(self):
        return f'<UnitOfMeasure {self.name} ({self.abbreviation})>'

class Product(BaseModel):
    __tablename__ = 'products'
    
    # Basic Information
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    barcode = db.Column(db.String(50))
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    
    # Classification
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    product_type = db.Column(db.String(20), default='physical')  # physical, service, digital
    
    # Pricing
    cost_price = db.Column(db.Numeric(10, 2))
    selling_price = db.Column(db.Numeric(10, 2), nullable=False)
    msrp = db.Column(db.Numeric(10, 2))
    wholesale_price = db.Column(db.Numeric(10, 2))
    
    # Inventory
    track_inventory = db.Column(db.Boolean, default=True)
    current_stock = db.Column(db.Integer, default=0)
    reserved_stock = db.Column(db.Integer, default=0)
    available_stock = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=0)
    max_stock_level = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=0)
    reorder_quantity = db.Column(db.Integer, default=0)
    
    # Units and Measurements
    base_unit_id = db.Column(db.Integer, db.ForeignKey('units_of_measure.id'))
    weight = db.Column(db.Numeric(8, 3))
    length = db.Column(db.Numeric(8, 3))
    width = db.Column(db.Numeric(8, 3))
    height = db.Column(db.Numeric(8, 3))
    
    # Tax and Accounting
    tax_category = db.Column(db.String(50))
    is_taxable = db.Column(db.Boolean, default=True)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    
    # Status and Settings
    status = db.Column(db.String(20), default='active')
    is_featured = db.Column(db.Boolean, default=False)
    allow_backorder = db.Column(db.Boolean, default=False)
    
    # Supplier Information
    primary_supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier_sku = db.Column(db.String(50))
    lead_time_days = db.Column(db.Integer, default=0)
    
    # Relationships
    category = db.relationship('ProductCategory', backref='products')
    brand = db.relationship('Brand', backref='products')
    base_unit = db.relationship('UnitOfMeasure', backref='products')
    primary_supplier = db.relationship('Supplier', backref='supplied_products')

    @property
    def stock_status(self):
        """Get stock status based on current levels"""
        if not self.track_inventory:
            return 'not_tracked'
        elif self.current_stock <= 0:
            return 'out_of_stock'
        elif self.current_stock <= self.min_stock_level:
            return 'low_stock'
        else:
            return 'in_stock'

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price and self.selling_price:
            return ((self.selling_price - self.cost_price) / self.selling_price) * 100
        return 0

    def update_available_stock(self):
        """Update available stock (current - reserved)"""
        self.available_stock = max(0, self.current_stock - self.reserved_stock)

    def __repr__(self):
        return f'<Product {self.sku}: {self.name}>'

class Warehouse(BaseModel):
    __tablename__ = 'warehouses'
    
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True)
    
    manager = db.relationship('User', backref='managed_warehouses')

    def __repr__(self):
        return f'<Warehouse {self.code}: {self.name}>'

class StockMovement(BaseModel):
    __tablename__ = 'stock_movements'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # in, out, transfer, adjustment
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    reference_type = db.Column(db.String(50))  # sales_order, purchase_order, adjustment, transfer
    reference_id = db.Column(db.Integer)
    notes = db.Column(db.Text)
    movement_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    product = db.relationship('Product', backref='stock_movements')
    warehouse = db.relationship('Warehouse', backref='stock_movements')
    created_by = db.relationship('User', backref='stock_movements')

    @property
    def total_value(self):
        """Calculate total value of movement"""
        if self.unit_cost:
            return abs(self.quantity) * self.unit_cost
        return 0

    def __repr__(self):
        return f'<StockMovement {self.movement_type}: {self.quantity} of Product {self.product_id}>'

class StockAdjustment(BaseModel):
    __tablename__ = 'stock_adjustments'
    
    adjustment_number = db.Column(db.String(20), unique=True, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    adjustment_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, approved, posted
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    warehouse = db.relationship('Warehouse', backref='stock_adjustments')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_adjustments')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_adjustments')

    def __repr__(self):
        return f'<StockAdjustment {self.adjustment_number}>'

class StockAdjustmentItem(BaseModel):
    __tablename__ = 'stock_adjustment_items'
    
    adjustment_id = db.Column(db.Integer, db.ForeignKey('stock_adjustments.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    current_quantity = db.Column(db.Integer, nullable=False)
    adjusted_quantity = db.Column(db.Integer, nullable=False)
    variance = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    
    adjustment = db.relationship('StockAdjustment', backref='items')
    product = db.relationship('Product', backref='adjustment_items')

    @property
    def variance_value(self):
        """Calculate variance value"""
        if self.unit_cost:
            return self.variance * self.unit_cost
        return 0

    def __repr__(self):
        return f'<StockAdjustmentItem Adj:{self.adjustment_id} Product:{self.product_id}>'

# Auto-generate codes
@event.listens_for(ProductCategory, 'before_insert')
def generate_category_code(mapper, connection, target):
    if not target.code:
        # Generate code from name
        code = ''.join(word[:3].upper() for word in target.name.split()[:2])
        target.code = code

@event.listens_for(Warehouse, 'before_insert')
def generate_warehouse_code(mapper, connection, target):
    if not target.code:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(code, 3) AS INTEGER)) FROM warehouses WHERE code LIKE 'WH%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.code = f"WH{next_num:03d}"

@event.listens_for(StockAdjustment, 'before_insert')
def generate_adjustment_number(mapper, connection, target):
    if not target.adjustment_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(adjustment_number, 4) AS INTEGER)) FROM stock_adjustments WHERE adjustment_number LIKE 'ADJ%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.adjustment_number = f"ADJ{next_num:06d}"