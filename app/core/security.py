from functools import wraps
from flask import abort, session
from flask_login import current_user

class Permission:
    READ = 1
    WRITE = 2
    DELETE = 4
    ADMIN = 8

class Role:
    EMPLOYEE = Permission.READ
    MANAGER = Permission.READ | Permission.WRITE
    ADMIN = Permission.READ | Permission.WRITE | Permission.DELETE | Permission.ADMIN

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)