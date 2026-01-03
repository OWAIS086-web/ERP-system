from app.core.extensions import db
from app.models.base import BaseModel
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import event

class ChartOfAccounts(BaseModel):
    __tablename__ = 'chart_of_accounts'
    
    account_code = db.Column(db.String(20), unique=True, nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    parent_account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Self-referential relationship
    parent = db.relationship('ChartOfAccounts', remote_side='ChartOfAccounts.id', backref='sub_accounts')

    @property
    def full_account_name(self):
        """Get full account name with parent"""
        if self.parent:
            return f"{self.parent.account_name} - {self.account_name}"
        return self.account_name

    def __repr__(self):
        return f'<Account {self.account_code}: {self.account_name}>'

class Invoice(BaseModel):
    __tablename__ = 'invoices'
    
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    
    # Financial details
    subtotal = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Dates
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, overdue, cancelled
    
    # Payment tracking
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    balance_due = db.Column(db.Numeric(15, 2))
    
    # Notes
    notes = db.Column(db.Text)
    terms = db.Column(db.Text)
    
    # Relationships
    customer = db.relationship('Customer', backref='invoices')
    order = db.relationship('SalesOrder', backref='invoices')

    def calculate_totals(self):
        """Calculate invoice totals"""
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        self.balance_due = self.total_amount - self.paid_amount

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return date.today() > self.due_date and self.balance_due > 0

    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

class InvoiceItem(BaseModel):
    __tablename__ = 'invoice_items'
    
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    line_total = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Relationships
    invoice = db.relationship('Invoice', backref='items')
    product = db.relationship('Product', backref='invoice_items')

    def calculate_line_total(self):
        """Calculate line total with discount"""
        discounted_price = self.unit_price * (1 - self.discount_percentage / 100)
        self.line_total = self.quantity * discounted_price

    def __repr__(self):
        return f'<InvoiceItem Invoice:{self.invoice_id}>'

class Payment(BaseModel):
    __tablename__ = 'payments'
    
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(50), nullable=False)  # cash, credit_card, bank_transfer, check
    
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed, cancelled
    
    # Bank/Card details
    bank_account = db.Column(db.String(100))
    transaction_id = db.Column(db.String(100))
    
    # Relationships
    invoice = db.relationship('Invoice', backref='payments')
    customer = db.relationship('Customer', backref='payments')

    def __repr__(self):
        return f'<Payment {self.payment_number}: ${self.amount}>'

class Expense(BaseModel):
    __tablename__ = 'expenses'
    
    expense_number = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    
    vendor = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))
    
    # Tax information
    is_taxable = db.Column(db.Boolean, default=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    
    # Approval workflow
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, paid
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    # Accounting
    account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'))
    
    # Attachments
    receipt_path = db.Column(db.String(200))
    
    notes = db.Column(db.Text)
    
    # Relationships
    submitted_by = db.relationship('User', foreign_keys=[submitted_by_id], backref='submitted_expenses')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_expenses')
    account = db.relationship('ChartOfAccounts', backref='expenses')

    @property
    def total_amount(self):
        """Get total amount including tax"""
        return self.amount + (self.tax_amount or 0)

    def __repr__(self):
        return f'<Expense {self.expense_number}: {self.description}>'

class JournalEntry(BaseModel):
    __tablename__ = 'journal_entries'
    
    entry_number = db.Column(db.String(20), unique=True, nullable=False)
    entry_date = db.Column(db.Date, nullable=False, default=date.today)
    reference = db.Column(db.String(100))
    description = db.Column(db.Text)
    total_debit = db.Column(db.Numeric(15, 2), default=0)
    total_credit = db.Column(db.Numeric(15, 2), default=0)
    status = db.Column(db.String(20), default='draft')  # draft, posted, reversed
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_by = db.relationship('User', backref='journal_entries')

    @property
    def is_balanced(self):
        """Check if journal entry is balanced"""
        return abs(self.total_debit - self.total_credit) < 0.01

    def calculate_totals(self):
        """Calculate total debits and credits"""
        self.total_debit = sum(line.debit_amount for line in self.lines)
        self.total_credit = sum(line.credit_amount for line in self.lines)

    def __repr__(self):
        return f'<JournalEntry {self.entry_number}>'

class JournalEntryLine(BaseModel):
    __tablename__ = 'journal_entry_lines'
    
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'), nullable=False)
    description = db.Column(db.String(200))
    debit_amount = db.Column(db.Numeric(15, 2), default=0)
    credit_amount = db.Column(db.Numeric(15, 2), default=0)
    
    journal_entry = db.relationship('JournalEntry', backref='lines')
    account = db.relationship('ChartOfAccounts', backref='journal_lines')

    def __repr__(self):
        return f'<JournalEntryLine Entry:{self.journal_entry_id} Account:{self.account_id}>'

class Budget(BaseModel):
    __tablename__ = 'budgets'
    
    name = db.Column(db.String(100), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_budget = db.Column(db.Numeric(15, 2), default=0)
    status = db.Column(db.String(20), default='draft')  # draft, approved, active, closed
    
    def __repr__(self):
        return f'<Budget {self.name} FY{self.fiscal_year}>'

class BudgetLine(BaseModel):
    __tablename__ = 'budget_lines'
    
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'), nullable=False)
    budgeted_amount = db.Column(db.Numeric(15, 2), nullable=False)
    actual_amount = db.Column(db.Numeric(15, 2), default=0)
    variance = db.Column(db.Numeric(15, 2), default=0)
    
    budget = db.relationship('Budget', backref='lines')
    account = db.relationship('ChartOfAccounts', backref='budget_lines')

    @property
    def variance_percentage(self):
        """Calculate variance percentage"""
        if self.budgeted_amount:
            return (self.variance / self.budgeted_amount) * 100
        return 0

    def calculate_variance(self):
        """Calculate variance (actual - budgeted)"""
        self.variance = self.actual_amount - self.budgeted_amount

    def __repr__(self):
        return f'<BudgetLine Budget:{self.budget_id} Account:{self.account_id}>'

# Auto-generate numbers
@event.listens_for(Invoice, 'before_insert')
def generate_invoice_number(mapper, connection, target):
    if not target.invoice_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(invoice_number, 5) AS INTEGER)) FROM invoices WHERE invoice_number LIKE 'INV-%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.invoice_number = f"INV-{next_num:06d}"

@event.listens_for(Payment, 'before_insert')
def generate_payment_number(mapper, connection, target):
    if not target.payment_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(payment_number, 5) AS INTEGER)) FROM payments WHERE payment_number LIKE 'PAY-%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.payment_number = f"PAY-{next_num:06d}"

@event.listens_for(Expense, 'before_insert')
def generate_expense_number(mapper, connection, target):
    if not target.expense_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(expense_number, 5) AS INTEGER)) FROM expenses WHERE expense_number LIKE 'EXP-%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.expense_number = f"EXP-{next_num:06d}"

@event.listens_for(JournalEntry, 'before_insert')
def generate_journal_entry_number(mapper, connection, target):
    if not target.entry_number:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(entry_number, 3) AS INTEGER)) FROM journal_entries WHERE entry_number LIKE 'JE%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.entry_number = f"JE{next_num:06d}"