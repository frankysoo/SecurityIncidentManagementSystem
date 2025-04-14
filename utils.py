from functools import wraps
from flask import abort
from flask_login import current_user
from datetime import datetime, timedelta
import pytz
from app import db
from models import Incident, User, Activity

# Role-based access control
def requires_role(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Format datetime for display
def format_datetime(dt):
    if not dt:
        return ""
    
    # Assume UTC if no timezone
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

# Get incident metrics
def get_incident_metrics(time_period='all'):
    # Base query
    query = Incident.query
    
    # Apply time filter
    if time_period != 'all':
        if time_period == '7days':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif time_period == '30days':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif time_period == '90days':
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)  # Default to 30 days
        
        query = query.filter(Incident.created_at >= start_date)
    
    # Total incidents
    total_incidents = query.count()
    
    # Open incidents
    open_incidents = query.filter(Incident.status.in_(['open', 'in-progress'])).count()
    
    # Resolved incidents
    resolved_incidents = query.filter_by(status='resolved').count()
    
    # Incidents by severity
    critical = query.filter_by(severity='critical').count()
    high = query.filter_by(severity='high').count()
    medium = query.filter_by(severity='medium').count()
    low = query.filter_by(severity='low').count()
    
    # Average resolution time (in hours)
    avg_resolution_time = db.session.query(
        db.func.avg(db.func.julianday(Incident.resolution_time) - db.func.julianday(Incident.detection_time)) * 24
    ).filter(
        Incident.detection_time.isnot(None),
        Incident.resolution_time.isnot(None)
    ).scalar() or 0
    
    if not isinstance(avg_resolution_time, (int, float)):
        avg_resolution_time = 0
    
    # Recent activity count
    recent_activity_cutoff = datetime.utcnow() - timedelta(days=1)
    recent_activity = Activity.query.filter(Activity.created_at >= recent_activity_cutoff).count()
    
    return {
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'resolved_incidents': resolved_incidents,
        'critical': critical,
        'high': high,
        'medium': medium,
        'low': low,
        'avg_resolution_time': round(avg_resolution_time, 2),
        'recent_activity': recent_activity
    }

# Common options
incident_type_options = [
    'malware', 'phishing', 'data_breach', 'ddos', 'unauthorized_access',
    'ransomware', 'insider_threat', 'social_engineering', 'physical_security', 'other'
]

severity_options = [
    'critical', 'high', 'medium', 'low'
]

status_options = [
    'open', 'in-progress', 'contained', 'resolved', 'closed'
]

activity_type_options = [
    'detection', 'analysis', 'containment', 'eradication', 'recovery', 'post-incident'
]

# Get users that can be assigned to incidents
def get_assignable_users():
    return User.query.filter(User.role.in_(['admin', 'manager', 'analyst'])).all()
