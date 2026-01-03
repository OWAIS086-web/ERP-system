from app.core.extensions import db
from app.models.base import BaseModel
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import event

class ProjectCategory(BaseModel):
    __tablename__ = 'project_categories'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#667eea')  # Hex color code
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<ProjectCategory {self.name}>'

class Project(BaseModel):
    __tablename__ = 'projects'
    
    # Basic Information
    project_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('project_categories.id'))
    
    # Project Management
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    
    # Budget and Financial
    budget = db.Column(db.Numeric(15, 2), default=0)
    actual_cost = db.Column(db.Numeric(15, 2), default=0)
    billable_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Progress
    progress_percentage = db.Column(db.Numeric(5, 2), default=0)
    status = db.Column(db.String(20), default='planning')  # planning, active, on_hold, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Settings
    is_billable = db.Column(db.Boolean, default=True)
    is_template = db.Column(db.Boolean, default=False)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relationships
    category = db.relationship('ProjectCategory', backref='projects')
    manager = db.relationship('User', backref='managed_projects')
    client = db.relationship('Customer', backref='projects')

    @property
    def duration_days(self):
        """Calculate project duration in days"""
        return (self.end_date - self.start_date).days

    @property
    def budget_variance(self):
        """Calculate budget variance"""
        return self.budget - self.actual_cost

    @property
    def budget_variance_percentage(self):
        """Calculate budget variance percentage"""
        if self.budget > 0:
            return (self.budget_variance / self.budget) * 100
        return 0

    @property
    def is_overdue(self):
        """Check if project is overdue"""
        return date.today() > self.end_date and self.status not in ['completed', 'cancelled']

    def calculate_progress(self):
        """Calculate progress based on completed tasks"""
        if self.tasks:
            completed_tasks = len([task for task in self.tasks if task.status == 'completed'])
            total_tasks = len(self.tasks)
            self.progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    def __repr__(self):
        return f'<Project {self.project_code}: {self.name}>'

class ProjectTask(BaseModel):
    __tablename__ = 'project_tasks'
    
    # Task Information
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Assignment
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Dates
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    
    # Progress
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, review, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    progress_percentage = db.Column(db.Numeric(5, 2), default=0)
    
    # Time Tracking
    estimated_hours = db.Column(db.Numeric(6, 2), default=0)
    actual_hours = db.Column(db.Numeric(6, 2), default=0)
    
    # Dependencies
    parent_task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'))
    
    # Relationships
    project = db.relationship('Project', backref='tasks')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_tasks')
    parent_task = db.relationship('ProjectTask', remote_side='ProjectTask.id', backref='subtasks')

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        return (self.due_date and date.today() > self.due_date and 
                self.status not in ['completed', 'cancelled'])

    @property
    def hours_variance(self):
        """Calculate hours variance"""
        return self.estimated_hours - self.actual_hours

    def __repr__(self):
        return f'<ProjectTask {self.name} (Project: {self.project_id})>'

class TimeEntry(BaseModel):
    __tablename__ = 'time_entries'
    
    # Entry Information
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Time Details
    date = db.Column(db.Date, nullable=False, default=date.today)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    hours = db.Column(db.Numeric(6, 2), nullable=False)
    
    # Description
    description = db.Column(db.Text)
    
    # Billing
    is_billable = db.Column(db.Boolean, default=True)
    hourly_rate = db.Column(db.Numeric(8, 2))
    billable_amount = db.Column(db.Numeric(10, 2))
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, submitted, approved, billed
    
    # Relationships
    project = db.relationship('Project', backref='time_entries')
    task = db.relationship('ProjectTask', backref='time_entries')
    user = db.relationship('User', backref='time_entries')

    def calculate_billable_amount(self):
        """Calculate billable amount"""
        if self.is_billable and self.hourly_rate:
            self.billable_amount = self.hours * self.hourly_rate

    def __repr__(self):
        return f'<TimeEntry {self.user_id}: {self.hours}h on {self.date}>'

class ProjectMilestone(BaseModel):
    __tablename__ = 'project_milestones'
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Dates
    due_date = db.Column(db.Date, nullable=False)
    completed_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, completed, overdue
    
    # Relationships
    project = db.relationship('Project', backref='milestones')

    @property
    def is_overdue(self):
        """Check if milestone is overdue"""
        return date.today() > self.due_date and self.status != 'completed'

    def __repr__(self):
        return f'<ProjectMilestone {self.name} (Project: {self.project_id})>'

class ProjectResource(BaseModel):
    __tablename__ = 'project_resources'
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Role and Allocation
    role = db.Column(db.String(100))
    allocation_percentage = db.Column(db.Numeric(5, 2), default=100)  # % of time allocated
    hourly_rate = db.Column(db.Numeric(8, 2))
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    project = db.relationship('Project', backref='resources')
    user = db.relationship('User', backref='project_assignments')

    def __repr__(self):
        return f'<ProjectResource Project:{self.project_id} User:{self.user_id}>'

class ProjectDocument(BaseModel):
    __tablename__ = 'project_documents'
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # File Information
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    
    # Metadata
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    version = db.Column(db.String(20), default='1.0')
    
    # Relationships
    project = db.relationship('Project', backref='documents')
    uploaded_by = db.relationship('User', backref='uploaded_documents')

    def __repr__(self):
        return f'<ProjectDocument {self.name} (Project: {self.project_id})>'

class ProjectExpense(BaseModel):
    __tablename__ = 'project_expenses'
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    
    # Billing
    is_billable = db.Column(db.Boolean, default=False)
    markup_percentage = db.Column(db.Numeric(5, 2), default=0)
    billable_amount = db.Column(db.Numeric(10, 2))
    
    # Approval
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Receipt
    receipt_path = db.Column(db.String(500))
    
    # Relationships
    project = db.relationship('Project', backref='expenses')
    submitted_by = db.relationship('User', backref='project_expenses')

    def calculate_billable_amount(self):
        """Calculate billable amount with markup"""
        if self.is_billable:
            markup = self.amount * (self.markup_percentage / 100)
            self.billable_amount = self.amount + markup

    def __repr__(self):
        return f'<ProjectExpense {self.description}: ${self.amount}>'

# Auto-generate codes
@event.listens_for(Project, 'before_insert')
def generate_project_code(mapper, connection, target):
    if not target.project_code:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(project_code, 5) AS INTEGER)) FROM projects WHERE project_code LIKE 'PROJ%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.project_code = f"PROJ{next_num:06d}"