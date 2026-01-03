from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.projects import bp
from app.projects.models import (
    Project, ProjectCategory, ProjectTask, TimeEntry, 
    ProjectMilestone, ProjectResource, ProjectDocument, ProjectExpense
)
from app.sales.models import Customer
from app.models.user import User
from app.core.extensions import db
from datetime import datetime, date
from decimal import Decimal

@bp.route('/')
@login_required
def index():
    """Project dashboard with overview statistics"""
    projects = Project.query.filter_by(is_deleted=False).all()
    
    # Calculate statistics
    active_projects = len([p for p in projects if p.status == 'active'])
    completed_projects = len([p for p in projects if p.status == 'completed'])
    overdue_projects = len([p for p in projects if p.end_date < date.today() and p.status not in ['completed', 'cancelled']])
    
    # Get recent projects
    recent_projects = Project.query.filter_by(is_deleted=False).order_by(Project.created_at.desc()).limit(10).all()
    
    return render_template('projects/index.html', 
                         projects=recent_projects,
                         active_count=active_projects,
                         completed_count=completed_projects,
                         overdue_count=overdue_projects,
                         total_projects=len(projects))

@bp.route('/list')
@login_required
def project_list():
    """Complete project list with filtering"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Project.query.filter_by(is_deleted=False)
    
    if status_filter:
        query = query.filter(Project.status == status_filter)
    if category_filter:
        query = query.filter(Project.category_id == category_filter)
    if search:
        query = query.filter(Project.name.contains(search))
    
    projects = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    categories = ProjectCategory.query.filter_by(is_deleted=False).all()
    
    return render_template('projects/list.html', 
                         projects=projects,
                         categories=categories,
                         status_filter=status_filter,
                         category_filter=category_filter,
                         search=search)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create new project"""
    if request.method == 'POST':
        try:
            # Generate project code
            last_project = Project.query.order_by(Project.id.desc()).first()
            next_number = (last_project.id + 1) if last_project else 1
            project_code = f"PROJ{next_number:06d}"
            
            project = Project(
                project_code=project_code,
                name=request.form['name'],
                description=request.form.get('description', ''),
                category_id=request.form.get('category_id') or None,
                manager_id=request.form['manager_id'],
                client_id=request.form.get('client_id') or None,
                start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
                budget=Decimal(request.form.get('budget', 0)),
                status=request.form.get('status', 'planning'),
                priority=request.form.get('priority', 'medium'),
                is_billable=bool(request.form.get('is_billable'))
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects.project_detail', id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating project: {str(e)}', 'error')
    
    categories = ProjectCategory.query.filter_by(is_deleted=False).all()
    managers = User.query.filter_by(is_active=True).all()
    clients = Customer.query.filter_by(is_deleted=False).all()
    
    return render_template('projects/create.html',
                         categories=categories,
                         managers=managers,
                         clients=clients)

@bp.route('/<int:id>')
@login_required
def project_detail(id):
    """Project detail view with tasks, milestones, and progress"""
    project = Project.query.get_or_404(id)
    
    # Get project tasks
    tasks = ProjectTask.query.filter_by(project_id=id, is_deleted=False).all()
    
    # Get project milestones
    milestones = ProjectMilestone.query.filter_by(project_id=id, is_deleted=False).order_by(ProjectMilestone.due_date).all()
    
    # Get recent time entries
    recent_time_entries = TimeEntry.query.filter_by(project_id=id, is_deleted=False).order_by(TimeEntry.date.desc()).limit(10).all()
    
    # Get project resources
    resources = ProjectResource.query.filter_by(project_id=id, is_deleted=False).all()
    
    # Calculate progress statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == 'completed'])
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return render_template('projects/detail.html',
                         project=project,
                         tasks=tasks,
                         milestones=milestones,
                         time_entries=recent_time_entries,
                         resources=resources,
                         progress_percentage=progress_percentage)

@bp.route('/<int:id>/tasks')
@login_required
def project_tasks(id):
    """Project tasks management"""
    project = Project.query.get_or_404(id)
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    assignee_filter = request.args.get('assignee', '')
    
    query = ProjectTask.query.filter_by(project_id=id, is_deleted=False)
    
    if status_filter:
        query = query.filter(ProjectTask.status == status_filter)
    if priority_filter:
        query = query.filter(ProjectTask.priority == priority_filter)
    if assignee_filter:
        query = query.filter(ProjectTask.assigned_to_id == assignee_filter)
    
    tasks = query.order_by(ProjectTask.priority.desc(), ProjectTask.due_date).paginate(
        page=page, per_page=20, error_out=False)
    
    team_members = User.query.filter_by(is_active=True).all()
    
    return render_template('projects/tasks.html',
                         project=project,
                         tasks=tasks,
                         team_members=team_members,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         assignee_filter=assignee_filter)

@bp.route('/<int:id>/time-entries')
@login_required
def project_time_entries(id):
    """Project time tracking"""
    project = Project.query.get_or_404(id)
    
    page = request.args.get('page', 1, type=int)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    user_filter = request.args.get('user', '')
    
    query = TimeEntry.query.filter_by(project_id=id, is_deleted=False)
    
    if date_from:
        query = query.filter(TimeEntry.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(TimeEntry.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    if user_filter:
        query = query.filter(TimeEntry.user_id == user_filter)
    
    time_entries = query.order_by(TimeEntry.date.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Calculate totals
    total_hours = sum([entry.hours for entry in query.all()])
    billable_hours = sum([entry.hours for entry in query.all() if entry.is_billable])
    
    team_members = User.query.filter_by(is_active=True).all()
    
    return render_template('projects/time_entries.html',
                         project=project,
                         time_entries=time_entries,
                         team_members=team_members,
                         total_hours=total_hours,
                         billable_hours=billable_hours,
                         date_from=date_from,
                         date_to=date_to,
                         user_filter=user_filter)

@bp.route('/<int:id>/milestones')
@login_required
def project_milestones(id):
    """Project milestones management"""
    project = Project.query.get_or_404(id)
    
    milestones = ProjectMilestone.query.filter_by(project_id=id, is_deleted=False).order_by(ProjectMilestone.due_date).all()
    
    # Calculate milestone statistics
    total_milestones = len(milestones)
    completed_milestones = len([m for m in milestones if m.status == 'completed'])
    overdue_milestones = len([m for m in milestones if m.due_date < date.today() and m.status != 'completed'])
    
    return render_template('projects/milestones.html',
                         project=project,
                         milestones=milestones,
                         total_milestones=total_milestones,
                         completed_milestones=completed_milestones,
                         overdue_milestones=overdue_milestones)

@bp.route('/<int:id>/resources')
@login_required
def project_resources(id):
    """Project resource allocation"""
    project = Project.query.get_or_404(id)
    
    resources = ProjectResource.query.filter_by(project_id=id, is_deleted=False).all()
    available_users = User.query.filter_by(is_active=True).all()
    
    return render_template('projects/resources.html',
                         project=project,
                         resources=resources,
                         available_users=available_users)

@bp.route('/<int:id>/documents')
@login_required
def project_documents(id):
    """Project document management"""
    project = Project.query.get_or_404(id)
    
    documents = ProjectDocument.query.filter_by(project_id=id, is_deleted=False).order_by(ProjectDocument.created_at.desc()).all()
    
    return render_template('projects/documents.html',
                         project=project,
                         documents=documents)

@bp.route('/<int:id>/expenses')
@login_required
def project_expenses(id):
    """Project expense tracking"""
    project = Project.query.get_or_404(id)
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = ProjectExpense.query.filter_by(project_id=id, is_deleted=False)
    
    if status_filter:
        query = query.filter(ProjectExpense.status == status_filter)
    
    expenses = query.order_by(ProjectExpense.expense_date.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Calculate totals
    total_expenses = sum([exp.amount for exp in query.all()])
    approved_expenses = sum([exp.amount for exp in query.all() if exp.status == 'approved'])
    
    return render_template('projects/expenses.html',
                         project=project,
                         expenses=expenses,
                         total_expenses=total_expenses,
                         approved_expenses=approved_expenses,
                         status_filter=status_filter)

@bp.route('/categories')
@login_required
def categories():
    """Project categories management"""
    categories = ProjectCategory.query.filter_by(is_deleted=False).all()
    
    return render_template('projects/categories.html',
                         categories=categories)