import os
import logging

# Application settings
DEBUG = True
SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")  # For development only

# Database settings
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///security_incidents.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Security Classifications
SEVERITY_LEVELS = {
    'critical': {
        'description': 'Critical impact on business operations or data security',
        'response_time': '1 hour',
        'color': 'danger'
    },
    'high': {
        'description': 'Significant impact on operations or potential data loss',
        'response_time': '4 hours',
        'color': 'warning'
    },
    'medium': {
        'description': 'Limited impact on operations, minor data security concerns',
        'response_time': '24 hours',
        'color': 'primary'
    },
    'low': {
        'description': 'Minimal impact, routine security event',
        'response_time': '72 hours',
        'color': 'info'
    }
}

# Incident Types
INCIDENT_TYPES = {
    'malware': {
        'description': 'Malicious software detected on systems',
        'playbook_id': 1
    },
    'phishing': {
        'description': 'Deceptive attempts to steal user data',
        'playbook_id': 2
    },
    'data_breach': {
        'description': 'Unauthorized access to sensitive data',
        'playbook_id': 3
    },
    'ddos': {
        'description': 'Distributed Denial of Service attack',
        'playbook_id': 4
    },
    'unauthorized_access': {
        'description': 'Unauthorized system or account access',
        'playbook_id': 5
    },
    'ransomware': {
        'description': 'Malware that encrypts data and demands payment',
        'playbook_id': 6
    },
    'insider_threat': {
        'description': 'Malicious actions by internal personnel',
        'playbook_id': 7
    },
    'social_engineering': {
        'description': 'Psychological manipulation to gain information',
        'playbook_id': 8
    },
    'physical_security': {
        'description': 'Physical security breaches or incidents',
        'playbook_id': 9
    },
    'other': {
        'description': 'Other security incidents not categorized above',
        'playbook_id': None
    }
}

# Team Role Options
TEAM_ROLES = [
    'Incident Commander',
    'Technical Lead',
    'Communications Lead',
    'Legal Advisor',
    'Forensic Analyst',
    'Scribe',
    'Executive Liaison',
    'Business Continuity',
    'Security Analyst'
]

# Activity Types with descriptions
ACTIVITY_TYPES = {
    'detection': 'Initial detection and identification of the incident',
    'analysis': 'Investigation and understanding of the incident scope',
    'containment': 'Limiting the spread and impact of the incident',
    'eradication': 'Removing the threat from the environment',
    'recovery': 'Restoring systems to normal operation',
    'post-incident': 'Post-incident activities and lessons learned'
}
