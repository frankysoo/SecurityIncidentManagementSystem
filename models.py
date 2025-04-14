from datetime import datetime
from app import db
from flask_login import UserMixin
import json
from sqlalchemy.ext.mutable import MutableDict, MutableList

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    role = db.Column(db.String(20), default='analyst')  # admin, manager, analyst, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    incidents_created = db.relationship('Incident', backref='creator', lazy='dynamic', foreign_keys='Incident.created_by')
    incidents_assigned = db.relationship('Incident', backref='assignee', lazy='dynamic', foreign_keys='Incident.assigned_to')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    team_memberships = db.relationship('TeamMember', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

# Team Model
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('TeamMember', backref='team', lazy='dynamic')
    
    def __repr__(self):
        return f'<Team {self.name}>'

# Team Member Model (Join Table with Role)
class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Incident Commander, Technical Lead, Comms Lead, etc.
    
    def __repr__(self):
        return f'<TeamMember {self.role}>'

# Incident Model
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='open')  # open, in-progress, contained, resolved, closed
    severity = db.Column(db.String(20), nullable=False)  # critical, high, medium, low
    incident_type = db.Column(db.String(50), nullable=False)  # malware, phishing, data breach, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    assigned_team = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    resolution = db.Column(db.Text, nullable=True)
    detection_time = db.Column(db.DateTime, nullable=True)
    resolution_time = db.Column(db.DateTime, nullable=True)
    affected_systems = db.Column(MutableList.as_mutable(db.JSON), default=list)
    tags = db.Column(MutableList.as_mutable(db.JSON), default=list)
    
    # Relationships
    team = db.relationship('Team', backref='incidents')
    activities = db.relationship('Activity', backref='incident', lazy='dynamic')
    comments = db.relationship('Comment', backref='incident', lazy='dynamic')
    attachments = db.relationship('Attachment', backref='incident', lazy='dynamic')
    
    def __repr__(self):
        return f'<Incident {self.id}: {self.title}>'
    
    def time_to_resolve(self):
        if self.detection_time and self.resolution_time:
            return (self.resolution_time - self.detection_time).total_seconds() / 3600  # in hours
        return None

# Activity Model (for tracking incident response activities)
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # detection, analysis, containment, eradication, recovery
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='activities')
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.activity_type}>'

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comment {self.id}>'

# Attachment Model
class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='attachments')
    
    def __repr__(self):
        return f'<Attachment {self.filename}>'

# Playbook Model
class Playbook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    steps = db.Column(MutableList.as_mutable(db.JSON), default=list)  # List of step dictionaries
    
    # Relationship
    creator = db.relationship('User', backref='playbooks')
    
    def __repr__(self):
        return f'<Playbook {self.title}>'

# Communication Template Model
class CommunicationTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # internal, external, executive, customer
    incident_type = db.Column(db.String(50), nullable=True)  # Optional association with incident type
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    creator = db.relationship('User', backref='templates')
    
    def __repr__(self):
        return f'<Template {self.name}>'

# Post-Incident Review Model
class PIR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False)
    conducted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conducted_at = db.Column(db.DateTime, default=datetime.utcnow)
    summary = db.Column(db.Text, nullable=False)
    what_happened = db.Column(db.Text, nullable=False)
    what_went_well = db.Column(db.Text, nullable=False)
    what_went_poorly = db.Column(db.Text, nullable=False)
    root_cause = db.Column(db.Text, nullable=False)
    action_items = db.Column(MutableList.as_mutable(db.JSON), default=list)  # List of action item dictionaries
    lessons_learned = db.Column(db.Text, nullable=False)
    
    # Relationships
    incident = db.relationship('Incident', backref='pir')
    conductor = db.relationship('User', backref='pirs_conducted')
    
    def __repr__(self):
        return f'<PIR for Incident {self.incident_id}>'
