from app.core.extensions import db
from app.models.base import BaseModel
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import event

class SupplierCategory(BaseModel):
    __tablename__ = 'supplier_categories'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<SupplierCategory {self.name}>'

class Supplier(BaseModel):
    __tablename__ = 'suppliers'
    
    # Basic Information
    supplier_code = db.Column(db.String(20), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    title = db.Column(db.String(50))
    
    # Contact Information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Business Information
    tax_id = db.Column(db.String(50))
    registration_number = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('supplier_categories.id'))
    
    # Financial Terms
    payment_terms = db.Column(db.String(50), default='Net 30')
    currency = db.Column(db.String(3), default='USD')
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    
    # Performance Metrics
    rating = db.Column(db.Integer, default=0)  # 1-5 stars
    on_time_delivery_rate = db.Column(db.Numeric(5, 2), default=0)
    quality_rating = db.Column(db.Numeric(5, 2), default=0)
    total_orders = db.Column(db.Integer, default=0)
    total_value = db.Column(db.Numeric(15, 2), default=0)
    
    # Status
    status = db.Column(db.String(20), default='active')
    is_preferred = db.Column(db.Boolean, default=False)
    
    # Relationships
    category = db.relationship('SupplierCategory', backref='suppliers')

    @property
    def display_name(self):
        return f"{self.company_name} ({self.supplier_code})"

    @property
    def average_order_value(self):
        """Calculate average order value"""
        if self.total_orders > 0:
            return self.total_value / self.total_orders
        return 0

    def __repr__(self):
        return f'<Supplier {self.supplier_code}: {self.company_name}>'

class PurchaseRequisition(BaseModel):
    __tablename__ = 'purchase_requisitions'
    
    # Requisition Information
    requisition_number = db.Column(db.String(20), unique=True, nullable=False)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    
    # Dates
    requisition_date = db.Column(db.Date, nullable=False, default=date.today)
    required_date = db.Column(db.Date, nullable=False)
    
    # Financial Information
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Status and Approval
    status = db.Column(db.String(20), default='draft')  # draft, submitted, approved, rejected, converted
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Approval workflow
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Notes
    justification = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Relationships
    requested_by = db.relationship('User', foreign_keys=[requested_by_id], backref='purchase_requisitions')
    department = db.relationship('Department', backref='purchase_requisitions')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_requisitions')

    def calculate_total(self):
        """Calculate total amount from line items"""
        self.total_amount = sum(item.line_total for item in self.items)

    def __repr__(self):
        return f'<PurchaseRequisition {self.requisition_number}>'

class PurchaseRequisitionItem(BaseModel):
    __tablename__ = 'purchase_requisition_items'
    
    requisition_id = db.Column(db.Integer, db.ForeignKey('purchase_requisitions.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    estimated_unit_price = db.Column(db.Numeric(10, 2))
    line_total = db.Column(db.Numeric(15, 2))
    
    # Specifications
    specifications = db.Column(db.Text)
    preferred_supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    
    # Relationships
    requisition = db.relationship('PurchaseRequisition', backref='items')
    product = db.relationship('Product', backref='requisition_items')
    preferred_supplier = db.relationship('Supplier', backref='preferred_items')

    def calculate_line_total(self):
        """Calculate line total"""
        if self.estimated_unit_price:
            self.line_total = self.quantity * self.estimated_unit_price

    def __repr__(self):
        return f'<PurchaseRequisitionItem Req:{self.requisition_id}>'

class PurchaseOrder(BaseModel):
    __tablename__ = 'purchase_orders'
    
    # Order Information
    po_number = db.Column(db.String(20), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    requisition_id = db.Column(db.Integer, db.ForeignKey('purchase_requisitions.id'))
    
    # Dates
    order_date = db.Column(db.Date, nullable=False, default=date.today)
    required_date = db.Column(db.Date)
    expected_date = db.Column(db.Date)
    
    # Financial Information
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, confirmed, received, cancelled
    
    # Delivery Information
    delivery_address = db.Column(db.Text)
    shipping_method = db.Column(db.String(50))
    
    # Payment Terms
    payment_terms = db.Column(db.String(50))
    
    # Notes
    notes = db.Column(db.Text)
    terms_conditions = db.Column(db.Text)
    
    # Relationships
    supplier = db.relationship('Supplier', backref='purchase_orders')
    buyer = db.relationship('User', backref='purchase_orders')
    requisition = db.relationship('PurchaseRequisition', backref='purchase_orders')

    def calculate_totals(self):
        """Calculate order totals"""
        self.subtotal = sum(item.line_total for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount

    def __repr__(self):
        return f'<PurchaseOrder {self.po_number}>'

class PurchaseOrderItem(BaseModel):
    __tablename__ = 'purchase_order_items'
    
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Receiving tracking
    quantity_received = db.Column(db.Integer, default=0)
    quantity_pending = db.Column(db.Integer, default=0)
    
    # Relationships
    purchase_order = db.relationship('PurchaseOrder', backref='items')
    product = db.relationship('Product', backref='po_items')

    def calculate_line_total(self):
        """Calculate line total"""
        self.line_total = self.quantity * self.unit_price

    @property
    def quantity_outstanding(self):
        """Get quantity still to be received"""
        return self.quantity - self.quantity_received

    def __repr__(self):
        return f'<PurchaseOrderItem PO:{self.po_id} Product:{self.product_id}>'

class GoodsReceipt(BaseModel):
    __tablename__ = 'goods_receipts'
    
    # Receipt Information
    receipt_number = db.Column(db.String(20), unique=True, nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    received_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Dates
    receipt_date = db.Column(db.Date, nullable=False, default=date.today)
    
    # Delivery Information
    delivery_note_number = db.Column(db.String(50))
    carrier = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, completed, discrepancy
    
    # Notes
    notes = db.Column(db.Text)
    discrepancy_notes = db.Column(db.Text)
    
    # Relationships
    purchase_order = db.relationship('PurchaseOrder', backref='goods_receipts')
    supplier = db.relationship('Supplier', backref='goods_receipts')
    received_by = db.relationship('User', backref='goods_receipts')

    def __repr__(self):
        return f'<GoodsReceipt {self.receipt_number}>'

class GoodsReceiptItem(BaseModel):
    __tablename__ = 'goods_receipt_items'
    
    receipt_id = db.Column(db.Integer, db.ForeignKey('goods_receipts.id'), nullable=False)
    po_item_id = db.Column(db.Integer, db.ForeignKey('purchase_order_items.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity_ordered = db.Column(db.Integer, nullable=False)
    quantity_received = db.Column(db.Integer, nullable=False)
    quantity_rejected = db.Column(db.Integer, default=0)
    
    # Quality control
    quality_status = db.Column(db.String(20), default='accepted')  # accepted, rejected, pending
    rejection_reason = db.Column(db.Text)
    
    # Relationships
    receipt = db.relationship('GoodsReceipt', backref='items')
    po_item = db.relationship('PurchaseOrderItem', backref='receipt_items')
    product = db.relationship('Product', backref='receipt_items')

    @property
    def variance(self):
        """Calculate variance between ordered and received"""
        return self.quantity_received - self.quantity_ordered

    def __repr__(self):
        return f'<GoodsReceiptItem Receipt:{self.receipt_id} Product:{self.product_id}>'

class SupplierEvaluation(BaseModel):
    __tablename__ = 'supplier_evaluations'
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    evaluation_date = db.Column(db.Date, nullable=False, default=date.today)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Ratings (1-5 scale)
    quality_rating = db.Column(db.Numeric(3, 2))
    delivery_rating = db.Column(db.Numeric(3, 2))
    service_rating = db.Column(db.Numeric(3, 2))
    price_rating = db.Column(db.Numeric(3, 2))
    overall_rating = db.Column(db.Numeric(3, 2))
    
    # Comments
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, completed
    
    # Relationships
    supplier = db.relationship('Supplier', backref='evaluations')
    evaluator = db.relationship('User', backref='supplier_evaluations')

    def calculate_overall_rating(self):
        """Calculate overall rating as average of individual ratings"""
        ratings = [r for r in [self.quality_rating, self.delivery_rating, 
                              self.service_rating, self.price_rating] if r is not None]
        if ratings:
            self.overall_rating = sum(ratings) / len(ratings)

    def __repr__(self):
        return f'<SupplierEvaluation Supplier:{self.supplier_id} Date:{self.evaluation_date}>'

# Auto-generate codes
@event.listens_for(Supplier, 'before_insert')
def generate_supplier_code(mapper, connection, target):
    if not target.supplier_code:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(supplier_code, 5) AS INTEGER)) FROM suppliers WHERE supplier_code LIKE 'SUPP%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.supplier_code = f"SUPP{next_num:06d}"

@event.listens_for(PurchaseRequisition, 'before_insert')
def generate_requisition_number(mapper, connection, target):
    if not target.requisition_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(requisition_number, 3) AS INTEGER)) FROM purchase_requisitions WHERE requisition_number LIKE 'PR%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.requisition_number = f"PR{next_num:06d}"

@event.listens_for(PurchaseOrder, 'before_insert')
def generate_po_number(mapper, connection, target):
    if not target.po_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(po_number, 3) AS INTEGER)) FROM purchase_orders WHERE po_number LIKE 'PO%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.po_number = f"PO{next_num:06d}"

@event.listens_for(GoodsReceipt, 'before_insert')
def generate_receipt_number(mapper, connection, target):
    if not target.receipt_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(receipt_number, 3) AS INTEGER)) FROM goods_receipts WHERE receipt_number LIKE 'GR%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.receipt_number = f"GR{next_num:06d}"