from app.core.extensions import db
from app.models.base import BaseModel

class Company(BaseModel):
    __tablename__ = 'companies'
    
    name = db.Column(db.String(100), nullable=False)
    legal_name = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    registration_number = db.Column(db.String(50))
    
    # Contact information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Business details
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    founded_date = db.Column(db.Date)
    
    # Settings
    currency = db.Column(db.String(3), default='USD')
    timezone = db.Column(db.String(50), default='UTC')
    fiscal_year_start = db.Column(db.Integer, default=1)  # Month (1-12)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<Company {self.name}>'