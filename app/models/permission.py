from app.core.extensions import db
from app.models.base import BaseModel

class Permission(BaseModel):
    __tablename__ = 'permissions'
    
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    module = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Permission {self.name}>'