from datetime import datetime
from app.core.extensions import db
from app.models.user import User

class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        user = User.query.filter_by(email=email, is_active=True, is_deleted=False).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def register_user(data):
        """Register a new user"""
        try:
            # Check if user already exists
            if User.query.filter_by(email=data['email']).first():
                return None
            if User.query.filter_by(username=data['username']).first():
                return None
            
            user = User(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                department=data.get('department'),
                position=data.get('position'),
                role='employee'  # Default role
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            return None
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """Change user password"""
        if user.check_password(old_password):
            user.set_password(new_password)
            db.session.commit()
            return True
        return False