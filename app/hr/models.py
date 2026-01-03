from app.core.extensions import db
from app.models.base import BaseModel
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import event

class Department(BaseModel):
    __tablename__ = 'departments'
    
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    parent_department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    budget = db.Column(db.Numeric(15, 2), default=0)
    cost_center = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    
    # Self-referential relationship
    parent = db.relationship('Department', remote_side='Department.id', backref='sub_departments')
    manager = db.relationship('Employee', foreign_keys=[manager_id], backref='managed_departments')

    @property
    def employee_count(self):
        """Get number of employees in department"""
        return len([emp for emp in self.employees if emp.employment_status == 'active'])

    def __repr__(self):
        return f'<Department {self.code}: {self.name}>'

class JobPosition(BaseModel):
    __tablename__ = 'job_positions'
    
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    responsibilities = db.Column(db.Text)
    
    # Compensation
    min_salary = db.Column(db.Numeric(10, 2))
    max_salary = db.Column(db.Numeric(10, 2))
    salary_currency = db.Column(db.String(3), default='USD')
    
    # Classification
    job_level = db.Column(db.String(20))  # entry, junior, senior, lead, manager, director
    employment_type = db.Column(db.String(20), default='full_time')  # full_time, part_time, contract
    
    is_active = db.Column(db.Boolean, default=True)
    
    department = db.relationship('Department', backref='positions')

    @property
    def salary_range(self):
        """Get formatted salary range"""
        if self.min_salary and self.max_salary:
            return f"${self.min_salary:,.0f} - ${self.max_salary:,.0f}"
        return "Not specified"

    def __repr__(self):
        return f'<JobPosition {self.code}: {self.title}>'

class Employee(BaseModel):
    __tablename__ = 'employees'
    
    # Personal Information
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    nationality = db.Column(db.String(50))
    
    # Identification
    national_id = db.Column(db.String(50))
    passport_number = db.Column(db.String(50))
    social_security_number = db.Column(db.String(50))
    
    # Contact Information
    personal_email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(50))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Employment Information
    hire_date = db.Column(db.Date, nullable=False)
    termination_date = db.Column(db.Date)
    employment_type = db.Column(db.String(20), default='full_time')  # full_time, part_time, contract, intern
    employment_status = db.Column(db.String(20), default='active')  # active, inactive, terminated, on_leave
    
    # Job Information
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    work_location = db.Column(db.String(100))
    
    # Compensation
    base_salary = db.Column(db.Numeric(10, 2))
    hourly_rate = db.Column(db.Numeric(8, 2))
    pay_frequency = db.Column(db.String(20), default='monthly')  # weekly, bi_weekly, monthly, annual
    currency = db.Column(db.String(3), default='USD')
    
    # Benefits and Leave
    vacation_days_total = db.Column(db.Integer, default=0)
    vacation_days_used = db.Column(db.Integer, default=0)
    sick_days_total = db.Column(db.Integer, default=0)
    sick_days_used = db.Column(db.Integer, default=0)
    personal_days_total = db.Column(db.Integer, default=0)
    personal_days_used = db.Column(db.Integer, default=0)
    
    # Performance
    performance_rating = db.Column(db.Numeric(3, 2))  # 1.00 to 5.00
    last_review_date = db.Column(db.Date)
    next_review_date = db.Column(db.Date)
    
    # Relationships
    user = db.relationship('User', backref='employee_profile')
    department = db.relationship('Department', foreign_keys=[department_id], backref='employees')
    position = db.relationship('JobPosition', backref='employees')
    manager = db.relationship('Employee', remote_side='Employee.id', foreign_keys=[manager_id], backref='direct_reports')

    @property
    def full_name(self):
        """Get employee's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def years_of_service(self):
        """Calculate years of service"""
        end_date = self.termination_date or date.today()
        return (end_date - self.hire_date).days / 365.25

    @property
    def vacation_days_remaining(self):
        """Get remaining vacation days"""
        return max(0, self.vacation_days_total - self.vacation_days_used)

    @property
    def sick_days_remaining(self):
        """Get remaining sick days"""
        return max(0, self.sick_days_total - self.sick_days_used)

    def __repr__(self):
        return f'<Employee {self.employee_id}: {self.full_name}>'

class LeaveType(BaseModel):
    __tablename__ = 'leave_types'
    
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_paid = db.Column(db.Boolean, default=True)
    max_days_per_year = db.Column(db.Integer)
    requires_approval = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<LeaveType {self.code}: {self.name}>'

class LeaveRequest(BaseModel):
    __tablename__ = 'leave_requests'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    approved_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Relationships
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='leave_requests')
    leave_type = db.relationship('LeaveType', backref='leave_requests')
    approved_by = db.relationship('Employee', foreign_keys=[approved_by_id], backref='approved_leave_requests')

    def calculate_days(self):
        """Calculate number of days requested"""
        self.days_requested = (self.end_date - self.start_date).days + 1

    def __repr__(self):
        return f'<LeaveRequest {self.employee_id}: {self.start_date} to {self.end_date}>'

class Attendance(BaseModel):
    __tablename__ = 'attendance'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Time tracking
    clock_in = db.Column(db.Time)
    clock_out = db.Column(db.Time)
    break_start = db.Column(db.Time)
    break_end = db.Column(db.Time)
    
    # Calculated fields
    hours_worked = db.Column(db.Numeric(4, 2), default=0)
    overtime_hours = db.Column(db.Numeric(4, 2), default=0)
    
    # Status
    status = db.Column(db.String(20), default='present')  # present, absent, late, half_day, holiday
    notes = db.Column(db.Text)
    
    # Relationships
    employee = db.relationship('Employee', backref='attendance_records')

    def calculate_hours(self):
        """Calculate hours worked"""
        if self.clock_in and self.clock_out:
            # Convert to datetime for calculation
            clock_in_dt = datetime.combine(date.today(), self.clock_in)
            clock_out_dt = datetime.combine(date.today(), self.clock_out)
            
            # Handle overnight shifts
            if clock_out_dt < clock_in_dt:
                clock_out_dt += timedelta(days=1)
            
            total_minutes = (clock_out_dt - clock_in_dt).total_seconds() / 60
            
            # Subtract break time if applicable
            if self.break_start and self.break_end:
                break_start_dt = datetime.combine(date.today(), self.break_start)
                break_end_dt = datetime.combine(date.today(), self.break_end)
                break_minutes = (break_end_dt - break_start_dt).total_seconds() / 60
                total_minutes -= break_minutes
            
            self.hours_worked = round(total_minutes / 60, 2)
            
            # Calculate overtime (over 8 hours)
            if self.hours_worked > 8:
                self.overtime_hours = self.hours_worked - 8
            else:
                self.overtime_hours = 0

    def __repr__(self):
        return f'<Attendance {self.employee_id}: {self.date}>'

class Payroll(BaseModel):
    __tablename__ = 'payroll'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    pay_date = db.Column(db.Date, nullable=False)
    
    # Earnings
    base_salary = db.Column(db.Numeric(10, 2), default=0)
    overtime_pay = db.Column(db.Numeric(10, 2), default=0)
    bonus = db.Column(db.Numeric(10, 2), default=0)
    commission = db.Column(db.Numeric(10, 2), default=0)
    allowances = db.Column(db.Numeric(10, 2), default=0)
    gross_pay = db.Column(db.Numeric(10, 2), default=0)
    
    # Deductions
    tax_deduction = db.Column(db.Numeric(10, 2), default=0)
    social_security = db.Column(db.Numeric(10, 2), default=0)
    health_insurance = db.Column(db.Numeric(10, 2), default=0)
    retirement_contribution = db.Column(db.Numeric(10, 2), default=0)
    other_deductions = db.Column(db.Numeric(10, 2), default=0)
    total_deductions = db.Column(db.Numeric(10, 2), default=0)
    
    # Net pay
    net_pay = db.Column(db.Numeric(10, 2), default=0)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, approved, paid
    
    # Relationships
    employee = db.relationship('Employee', backref='payroll_records')

    def calculate_totals(self):
        """Calculate gross pay, total deductions, and net pay"""
        self.gross_pay = (self.base_salary + self.overtime_pay + self.bonus + 
                         self.commission + self.allowances)
        
        self.total_deductions = (self.tax_deduction + self.social_security + 
                               self.health_insurance + self.retirement_contribution + 
                               self.other_deductions)
        
        self.net_pay = self.gross_pay - self.total_deductions

    def __repr__(self):
        return f'<Payroll {self.employee_id}: {self.pay_period_start} to {self.pay_period_end}>'

class PerformanceReview(BaseModel):
    __tablename__ = 'performance_reviews'
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)
    review_date = db.Column(db.Date, nullable=False)
    
    # Ratings (1-5 scale)
    overall_rating = db.Column(db.Numeric(3, 2))
    technical_skills = db.Column(db.Numeric(3, 2))
    communication = db.Column(db.Numeric(3, 2))
    teamwork = db.Column(db.Numeric(3, 2))
    leadership = db.Column(db.Numeric(3, 2))
    initiative = db.Column(db.Numeric(3, 2))
    
    # Comments
    strengths = db.Column(db.Text)
    areas_for_improvement = db.Column(db.Text)
    goals = db.Column(db.Text)
    employee_comments = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, completed, acknowledged
    
    # Relationships
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='performance_reviews')
    reviewer = db.relationship('Employee', foreign_keys=[reviewer_id], backref='conducted_reviews')

    def __repr__(self):
        return f'<PerformanceReview {self.employee_id}: {self.review_date}>'

# Auto-generate codes
@event.listens_for(Department, 'before_insert')
def generate_department_code(mapper, connection, target):
    if not target.code:
        # Generate code from name (first 3 letters of each word)
        words = target.name.split()
        code = ''.join(word[:3].upper() for word in words[:2])
        target.code = code

@event.listens_for(JobPosition, 'before_insert')
def generate_position_code(mapper, connection, target):
    if not target.code:
        # Generate code from title
        words = target.title.split()
        code = ''.join(word[:3].upper() for word in words[:2])
        target.code = code

@event.listens_for(Employee, 'before_insert')
def generate_employee_id(mapper, connection, target):
    if not target.employee_id:
        result = connection.execute(
            db.text("SELECT MAX(CAST(SUBSTR(employee_id, 4) AS INTEGER)) FROM employees WHERE employee_id LIKE 'EMP%'")
        ).scalar()
        next_num = (result or 0) + 1
        target.employee_id = f"EMP{next_num:06d}"

@event.listens_for(LeaveType, 'before_insert')
def generate_leave_type_code(mapper, connection, target):
    if not target.code:
        # Generate code from name
        words = target.name.split()
        code = ''.join(word[:2].upper() for word in words[:2])
        target.code = code