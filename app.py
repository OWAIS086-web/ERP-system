import os
import logging
from dotenv import load_dotenv
from app import create_app
from app.core.extensions import db
from app.models.user import User
from app.models.company import Company
from flask_moment import Moment

# Load environment variables
load_dotenv()

# Configure logging to reduce SQLAlchemy verbosity
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

# Create Flask app
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
moment = Moment(app)
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Company': Company}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        if not User.query.filter_by(email='admin@erp.com').first():
            admin = User(
                username='admin',
                email='admin@erp.com',
                first_name='System',
                last_name='Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin@erp.com / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)