from datetime import datetime
import uuid
import os
from werkzeug.utils import secure_filename

def generate_uuid():
    """Generate a unique identifier"""
    return str(uuid.uuid4())

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_date(date):
    """Format date for display"""
    if date:
        return date.strftime('%Y-%m-%d')
    return ''

def format_datetime(datetime_obj):
    """Format datetime for display"""
    if datetime_obj:
        return datetime_obj.strftime('%Y-%m-%d %H:%M')
    return ''

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, upload_folder):
    """Save uploaded file securely"""
    if file and allowed_file(file.filename, {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None

def paginate_query(query, page, per_page=20):
    """Paginate SQLAlchemy query"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )