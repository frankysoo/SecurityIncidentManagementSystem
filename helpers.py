from datetime import datetime, timedelta
from app import db
from models import Incident, Activity, Metric

def log_activity(incident_id, user_id, action, details=None):
    """Log an activity for an incident"""
    activity = Activity(
        incident_id=incident_id,
        user_id=user_id,
        action=action,
        details=details
    )
    db.session.add(activity)
    db.session.commit()
    return activity

def calculate_metrics(start_date=None, end_date=None):
    """Calculate key metrics for the dashboard or reports"""
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.utcnow().date()
        
    # Convert to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Ensure we include the full end date
    end_datetime = datetime.combine(end_date, datetime.max.time())
    start_datetime = datetime.combine(start_date, datetime.min.time())
    
    # Total number of incidents
    total_incidents = Incident.query.filter(
        Incident.created_at >= start_datetime,
        Incident.created_at <= end_datetime
    ).count()
    
    # Number of open incidents
    open_incidents = Incident.query.filter(
        Incident.created_at >= start_datetime,
        Incident.created_at <= end_datetime,
        Incident.status.in_(['New', 'Assigned', 'In Progress'])
    ).count()
    
    # Number of resolved incidents
    resolved_incidents = Incident.query.filter(
        Incident.created_at >= start_datetime,
        Incident.created_at <= end_datetime,
        Incident.status.in_(['Resolved', 'Closed'])
    ).count()
    
    # Calculate Mean Time to Resolution (MTTR) in hours
    resolved = Incident.query.filter(
        Incident.created_at >= start_datetime,
        Incident.created_at <= end_datetime,
        Incident.status.in_(['Resolved', 'Closed']),
        Incident.resolution_date.isnot(None)
    ).all()
    
    mttr = 0
    if resolved:
        total_resolution_time = sum(
            (incident.resolution_date - incident.created_at).total_seconds() / 3600
            for incident in resolved
        )
        mttr = total_resolution_time / len(resolved)
    
    # Incidents by severity
    critical = Incident.query.filter(
        Incident.created_at >= start_datetime,
        Incident.created_at <= end_datetime,
        Incident.severity == 'Critical'
    ).count()
    
    high = Incident.query.filter(
        Incident.created_at >= start_datetime,
        Incident.created_at <= end_datetime,
        Incident.severity == 'High'
    ).count()
    
    medium = Incident.query.filter(
        Incident.created_at >= start_datetime,
        Incident.created_at <= end_datetime,
        Incident.severity == 'Medium'
    ).count()
    
    low = Incident.query.filter(
        Incident.created_at >= start_datetime,
        Incident.created_at <= end_datetime,
        Incident.severity == 'Low'
    ).count()
    
    # Store metrics in the database for historical tracking
    today = datetime.utcnow().date()
    
    # Only store metrics once per day
    if not Metric.query.filter_by(date=today, name='Total Incidents').first():
        metrics_to_store = [
            Metric(name='Total Incidents', value=total_incidents, date=today, metric_type='Count'),
            Metric(name='Open Incidents', value=open_incidents, date=today, metric_type='Count'),
            Metric(name='Resolved Incidents', value=resolved_incidents, date=today, metric_type='Count'),
            Metric(name='MTTR', value=mttr, date=today, metric_type='Hours'),
            Metric(name='Critical Incidents', value=critical, date=today, metric_type='Count'),
            Metric(name='High Incidents', value=high, date=today, metric_type='Count'),
            Metric(name='Medium Incidents', value=medium, date=today, metric_type='Count'),
            Metric(name='Low Incidents', value=low, date=today, metric_type='Count')
        ]
        
        for metric in metrics_to_store:
            db.session.add(metric)
        
        db.session.commit()
    
    return {
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'resolved_incidents': resolved_incidents,
        'mttr': round(mttr, 2),
        'critical': critical,
        'high': high,
        'medium': medium,
        'low': low,
        'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    }

def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object to string"""
    if value is None:
        return ""
    return value.strftime(format)

def incident_to_dict(incident):
    """Convert an incident object to a dictionary"""
    return {
        'id': incident.id,
        'title': incident.title,
        'description': incident.description,
        'severity': incident.severity,
        'status': incident.status,
        'incident_type': incident.incident_type,
        'impact': incident.impact,
        'created_at': format_datetime(incident.created_at),
        'updated_at': format_datetime(incident.updated_at),
        'resolution_date': format_datetime(incident.resolution_date),
        'resolution': incident.resolution,
        'owner': incident.owner.full_name if incident.owner else None,
        'created_by': incident.created_by.full_name if incident.created_by else None,
        'assigned_to': incident.assigned_to.full_name if incident.assigned_to else None,
        'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in incident.tags],
        'teams': [{'id': team.id, 'name': team.name} for team in incident.teams]
    }

def get_severity_color(severity):
    """Get the color for a severity level"""
    colors = {
        'Critical': '#dc3545',  # Red
        'High': '#fd7e14',      # Orange
        'Medium': '#ffc107',    # Yellow
        'Low': '#28a745'        # Green
    }
    return colors.get(severity, '#6c757d')  # Default to gray

def get_status_color(status):
    """Get the color for a status level"""
    colors = {
        'New': '#0d6efd',       # Blue
        'Assigned': '#6610f2',  # Purple
        'In Progress': '#6f42c1', # Indigo
        'Resolved': '#20c997',  # Teal
        'Closed': '#6c757d'     # Gray
    }
    return colors.get(status, '#6c757d')  # Default to gray
