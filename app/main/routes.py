from flask import render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.main import bp
from app.core.extensions import db
from app.models.user import User

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get real dashboard statistics from database
    total_users = User.query.filter_by(is_deleted=False).count()
    active_users = User.query.filter_by(is_active=True, is_deleted=False).count()
    admin_users = User.query.filter_by(role='admin', is_deleted=False).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'inactive_users': total_users - active_users
    }
    
    # Get recent user activities (last 5 users created)
    recent_users = User.query.filter_by(is_deleted=False).order_by(User.created_at.desc()).limit(5).all()
    
    recent_activities = []
    for user in recent_users:
        activity = {
            'type': 'user',
            'description': f'New user registered: {user.full_name}',
            'time': user.created_at.strftime('%Y-%m-%d %H:%M'),
            'importance': 'normal' if user.role == 'employee' else 'important'
        }
        recent_activities.append(activity)
    
    return render_template('dashboard/index.html', stats=stats, recent_activities=recent_activities)

@bp.route('/notifications')
@login_required
def notifications():
    return render_template('notifications/index.html')

@bp.route('/activities')
@login_required
def activities():
    return render_template('activities/index.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile/index.html')

@bp.route('/settings')
@login_required
def settings():
    return render_template('settings/index.html')

@bp.route('/settings/notifications')
@login_required
def settings_notifications():
    return render_template('settings/index.html')

@bp.route('/settings/security')
@login_required
def settings_security():
    return render_template('settings/index.html')

@bp.route('/help')
@login_required
def help_page():
    return render_template('help/index.html')

@bp.route('/api/notifications')
@login_required
def api_notifications():
    # Mock notifications data
    notifications = [
        {
            'id': 1,
            'title': 'System Alert',
            'message': 'Database backup failed - immediate attention required',
            'type': 'critical',
            'read': False,
            'created_at': '2 minutes ago'
        },
        {
            'id': 2,
            'title': 'Payment Overdue',
            'message': 'Invoice #INV-001 is 5 days overdue',
            'type': 'warning',
            'read': False,
            'created_at': '1 hour ago'
        },
        {
            'id': 3,
            'title': 'Low Stock Alert',
            'message': '5 products are running low on inventory',
            'type': 'info',
            'read': False,
            'created_at': '3 hours ago'
        }
    ]
    
    unread_count = len([n for n in notifications if not n['read']])
    
    return jsonify({
        'notifications': notifications,
        'unread_count': unread_count
    })

@bp.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    # In a real app, you would update the database here
    return jsonify({'success': True})

@bp.route('/api/search', methods=['POST'])
@login_required
def api_search():
    from flask import request
    
    data = request.get_json()
    query = data.get('query', '').lower()
    
    # Mock search results
    all_results = [
        {
            'title': 'Dashboard',
            'description': 'Main dashboard with statistics and overview',
            'url': '/dashboard',
            'icon': 'fas fa-tachometer-alt',
            'category': 'Navigation'
        },
        {
            'title': 'Customers',
            'description': 'Manage customer information and contacts',
            'url': '/sales/customers',
            'icon': 'fas fa-users',
            'category': 'Sales'
        },
        {
            'title': 'Products',
            'description': 'Product catalog and inventory management',
            'url': '/inventory/products',
            'icon': 'fas fa-box',
            'category': 'Inventory'
        },
        {
            'title': 'Invoices',
            'description': 'Create and manage invoices',
            'url': '/finance/invoices',
            'icon': 'fas fa-file-invoice',
            'category': 'Finance'
        },
        {
            'title': 'Employees',
            'description': 'Employee management and HR functions',
            'url': '/hr/employees',
            'icon': 'fas fa-user-tie',
            'category': 'HR'
        }
    ]
    
    # Filter results based on query
    results = []
    for item in all_results:
        if (query in item['title'].lower() or 
            query in item['description'].lower() or 
            query in item['category'].lower()):
            results.append(item)
    
    return jsonify(results[:10])  # Limit to 10 results