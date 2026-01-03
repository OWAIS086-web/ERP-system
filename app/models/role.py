from app.core.extensions import db
from app.models.base import BaseModel

class Role(BaseModel):
    __tablename__ = 'roles'
    
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'