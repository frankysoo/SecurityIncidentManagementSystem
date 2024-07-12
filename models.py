from app import db
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

# Helper function for timezone-aware UTC timestamps
def utc_now():
    return datetime.now(timezone.utc)

# Association tables for many-to-many relationships
UserRole = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

IncidentRole = db.Table('incident_roles',
    db.Column('incident_id', db.Integer, db.ForeignKey('incident.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    last_login = db.Column(db.DateTime)

    # Relationships
    roles = db.relationship('Role', secondary=UserRole, backref=db.backref('users', lazy='dynamic'))
    incidents_created = db.relationship('Incident', backref='creator', lazy='dynamic', foreign_keys='Incident.created_by')
    incident_updates = db.relationship('IncidentUpdate', backref='user', lazy='dynamic')
    incident_roles = db.relationship('Role', secondary=IncidentRole, backref=db.backref('incident_users', lazy='dynamic'), overlaps="incidents")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def __repr__(self):
# Fixed bug: Corrected logic error
        return f'<User {self.username}>'

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))

    def __repr__(self):
        return f'<Role {self.name}>'

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False, index=True)  # Critical, High, Medium, Low
    status = db.Column(db.String(20), nullable=False, index=True)  # Open, Investigating, Contained, Eradicated, Resolved, Closed
    type = db.Column(db.String(64), nullable=False, index=True)  # Malware, Phishing, Data Breach, etc.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    detected_at = db.Column(db.DateTime, nullable=False)
    resolved_at = db.Column(db.DateTime)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    # Relationships
    updates = db.relationship('IncidentUpdate', backref='incident', lazy='dynamic', cascade='all, delete-orphan')
    pir = db.relationship('PIR', backref='incident', uselist=False, cascade='all, delete-orphan')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_incidents')

    # Team members with their roles
    team_members = db.relationship('User', secondary=IncidentRole, backref=db.backref('incidents', lazy='dynamic', overlaps="incident_roles,incident_users"), overlaps="incident_roles,incident_users")

    def __repr__(self):
        return f'<Incident {self.id}: {self.title}>'

class IncidentUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=utc_now)
    update_type = db.Column(db.String(20), nullable=False)  # Status Update, Action Taken, Note, etc.
    content = db.Column(db.Text, nullable=False)
    status_change = db.Column(db.String(20))  # If update changes incident status

    def __repr__(self):
        return f'<IncidentUpdate {self.id} for Incident {self.incident_id}>'

class Playbook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)
    incident_type = db.Column(db.String(64), nullable=False)
    severity_levels = db.Column(db.String(64), nullable=False)  # Comma-separated list of applicable severity levels
    created_at = db.Column(db.DateTime, default=utc_now)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    steps = db.relationship('PlaybookStep', backref='playbook', lazy='dynamic', cascade='all, delete-orphan', order_by='PlaybookStep.order')
    creator = db.relationship('User', backref='playbooks_created')

    def __repr__(self):
        return f'<Playbook {self.name}>'

class PlaybookStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playbook_id = db.Column(db.Integer, db.ForeignKey('playbook.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    actions = db.Column(db.Text, nullable=False)
    expected_outcome = db.Column(db.Text)
    role_responsible = db.Column(db.String(64))  # Which role should perform this step
    time_estimate = db.Column(db.String(64))  # Estimated time to complete

    def __repr__(self):
        return f'<PlaybookStep {self.order}: {self.title}>'

class CommunicationTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)
    template_type = db.Column(db.String(64), nullable=False)  # Internal Notification, External Notification, Status Update, etc.
    audience = db.Column(db.String(64), nullable=False)  # Executive, Technical Team, Customers, Public, etc.
    subject = db.Column(db.String(256))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    creator = db.relationship('User', backref='communication_templates_created')

    def __repr__(self):
        return f'<CommunicationTemplate {self.name}>'

class PIR(db.Model):
    """Post-Incident Review"""
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, unique=True)
    summary = db.Column(db.Text, nullable=False)
    timeline = db.Column(db.Text, nullable=False)
    impact_assessment = db.Column(db.Text, nullable=False)
    root_cause = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    scheduled_review_date = db.Column(db.DateTime)
    review_status = db.Column(db.String(20), default='Draft')  # Draft, Under Review, Approved, Rejected

    # Relationships
    findings = db.relationship('PIRFinding', backref='pir', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='pirs_created')

    def __repr__(self):
        return f'<PIR for Incident {self.incident_id}>'

class PIRFinding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pir_id = db.Column(db.Integer, db.ForeignKey('pir.id'), nullable=False)
    finding_type = db.Column(db.String(64), nullable=False)  # Improvement, Success, Failure, Risk
    description = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Completed

    # Relationships
    assignee = db.relationship('User', backref='pir_findings_assigned')

    def __repr__(self):
        return f'<PIRFinding {self.id} for PIR {self.pir_id}>'


def new_helper_function():
    """A new helper function."""
    return True
