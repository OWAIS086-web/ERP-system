from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.auth.services import AuthService
from app.models.user import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = AuthService.authenticate_user(email, password)
        if user:
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'department': request.form.get('department'),
            'position': request.form.get('position')
        }
        
        user = AuthService.register_user(data)
        if user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Email or username may already exist.', 'error')
    
    return render_template('auth/register.html')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if email:
            # In a real application, you would:
            # 1. Check if user exists
            # 2. Generate a secure reset token
            # 3. Send email with reset link
            # 4. Store token in database with expiration
            
            user = User.query.filter_by(email=email, is_deleted=False).first()
            if user:
                # Simulate sending email
                flash(f'Password reset instructions have been sent to {email}. Please check your inbox.', 'success')
            else:
                # Don't reveal if email exists for security
                flash(f'If an account with {email} exists, password reset instructions have been sent.', 'info')
            
            return redirect(url_for('auth.login'))
        else:
            flash('Please enter a valid email address.', 'error')
    
    return render_template('auth/forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # In a real application, you would validate the token here
    # For now, we'll just show a placeholder
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password and password == confirm_password:
            # In a real app, you would:
            # 1. Validate the token
            # 2. Update the user's password
            # 3. Invalidate the token
            flash('Your password has been reset successfully. Please log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Passwords do not match or are invalid.', 'error')
    
    return render_template('auth/reset_password.html', token=token)