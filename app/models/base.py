from datetime import datetime
from app.core.extensions import db

class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    def soft_delete(self):
        """Soft delete the record"""
        self.is_deleted = True
        db.session.commit()
    
    def restore(self):
        """Restore soft deleted record"""
        self.is_deleted = False
        db.session.commit()
    
    @classmethod
    def active(cls):
        """Query only active (non-deleted) records"""
        return cls.query.filter_by(is_deleted=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}