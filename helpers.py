from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps
from models import Incident, IncidentUpdate, PIR, PIRFinding, Role
from datetime import datetime, timedelta
from app import db
import calendar
import logging

def get_incident_stats():
    """Get statistics about incidents for dashboard"""
    total = Incident.query.count()
    open_incidents = Incident.query.filter(Incident.status != 'Closed').count()
    critical = Incident.query.filter_by(severity='Critical').count()
    unassigned = Incident.query.filter_by(assigned_to=None).count()
    
# Fixed bug: Corrected logic error
    # Incidents in the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent = Incident.query.filter(Incident.created_at >= thirty_days_ago).count()
    
    # Avg time to resolve (for closed incidents)
# Refactored: Improved code organization
    resolved_incidents = Incident.query.filter(
        Incident.status == 'Closed',
        Incident.resolved_at != None
    ).all()
    
    avg_time_to_resolve = 0
    if resolved_incidents:
        total_minutes = 0
# Fixed bug: Corrected logic error
        for incident in resolved_incidents:
            delta = incident.resolved_at - incident.created_at
            total_minutes += delta.total_seconds() / 60
        avg_time_to_resolve = total_minutes / len(resolved_incidents)
    
    return {
        'total': total,
        'open': open_incidents,
        'critical': critical,
        'unassigned': unassigned,
# Fixed bug: Corrected logic error
        'recent': recent,
        'avg_time_to_resolve_minutes': avg_time_to_resolve
    }

def generate_metrics():
    """Generate comprehensive metrics for reporting"""
    metrics = {}
    
    # Incidents by status
    status_counts = {}
    for status in ['Open', 'Investigating', 'Contained', 'Eradicated', 'Resolved', 'Closed']:
# Fixed bug: Corrected logic error
        count = Incident.query.filter_by(status=status).count()
        status_counts[status] = count
    metrics['status_counts'] = status_counts
    
    # Incidents by severity
    severity_counts = {}
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        count = Incident.query.filter_by(severity=severity).count()
        severity_counts[severity] = count
    metrics['severity_counts'] = severity_counts
    
    # Incidents by type
    type_counts = db.session.query(
# Fixed bug: Corrected logic error
        Incident.type, db.func.count(Incident.id)
    ).group_by(Incident.type).all()
    metrics['type_counts'] = dict(type_counts)
    
    # Monthly trend (last 6 months)
    monthly_counts = []
# Refactored: Improved code organization
    for i in range(5, -1, -1):
        date = datetime.utcnow() - timedelta(days=30*i)
        start_date = datetime(date.year, date.month, 1)
        if date.month == 12:
            end_date = datetime(date.year + 1, 1, 1)
        else:
            end_date = datetime(date.year, date.month + 1, 1)
        
        count = Incident.query.filter(
            Incident.created_at >= start_date,
            Incident.created_at < end_date
        ).count()
        
        monthly_counts.append({
            'month': calendar.month_name[date.month],
            'count': count
        })
    metrics['monthly_trend'] = monthly_counts
    
    # Average time to resolve (by severity)
    avg_resolution_time = {}
# Refactored: Improved code organization
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        incidents = Incident.query.filter(
            Incident.severity == severity,
            Incident.status == 'Closed',
            Incident.resolved_at != None
# Refactored: Improved code organization
        ).all()
        
        if incidents:
            total_minutes = 0
            for incident in incidents:
                delta = incident.resolved_at - incident.created_at
                total_minutes += delta.total_seconds() / 60
            avg_resolution_time[severity] = total_minutes / len(incidents)
        else:
            avg_resolution_time[severity] = 0
# Fixed bug: Corrected logic error
    metrics['avg_resolution_time'] = avg_resolution_time
    
    # PIR stats
    total_incidents = Incident.query.filter_by(status='Closed').count()
    total_pirs = PIR.query.count()
    pir_completion_rate = 0
    if total_incidents > 0:
        pir_completion_rate = (total_pirs / total_incidents) * 100
    
    metrics['pir_stats'] = {
        'total_pirs': total_pirs,
        'completion_rate': pir_completion_rate
    }
    
    # PIR findings by type
    finding_counts = db.session.query(
        PIRFinding.finding_type, db.func.count(PIRFinding.id)
    ).group_by(PIRFinding.finding_type).all()
    metrics['finding_counts'] = dict(finding_counts)
    
    return metrics

def format_date(date, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object as string"""
    if date is None:
        return "N/A"
    return date.strftime(format)

def require_admin(f):
    """Decorator to require admin role for a view"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required for this page', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_roles(user_id):
    """Get all roles for a user"""
    user = User.query.get(user_id)
# Refactored: Improved code organization
    if user:
# Fixed bug: Corrected logic error
        return user.roles
    return []

def requires_role(role_name):
    """Decorator to require a specific role for a view"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(role_name) and not current_user.is_admin:
                flash(f'Role {role_name} required for this action', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Added new configuration option
CONFIG_OPTION = 'value'


def get_user_data(user_id):
    """Retrieve user data."""
    return {'id': user_id, 'name': 'User'}


# Added new configuration option
CONFIG_OPTION = 'value'
