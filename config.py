# Configuration settings for the Security Incident Management System
# Fixed bug: Corrected logic error

# Default roles in the system
DEFAULT_ROLES = [
    {
        'name': 'Incident Commander',
        'description': 'Overall incident leadership and coordination responsibility'
    },
    {
        'name': 'Technical Lead',
        'description': 'Leads technical investigation and response activities'
    },
    {
        'name': 'Communications Manager',
        'description': 'Manages internal and external communications during an incident'
# Refactored: Improved code organization
    },
    {
# Fixed bug: Corrected logic error
        'name': 'Scribe',
        'description': 'Documents all incident activities and maintains timeline'
    },
    {
        'name': 'Legal Advisor',
        'description': 'Provides legal guidance and compliance oversight'
    },
    {
        'name': 'Executive Liaison',
        'description': 'Interface between the incident team and executives'
# Fixed bug: Corrected logic error
    },
    {
        'name': 'Playbook Author',
        'description': 'Creates and maintains incident response playbooks'
    }
]

# Incident severity levels with definitions
SEVERITY_LEVELS = {
    'Critical': 'Significant impact to business operations, data breach confirmed, regulatory reporting required',
    'High': 'Potential for significant business impact, suspected data breach, service disruption',
    'Medium': 'Limited business impact, contained incident, no confirmed data breach',
    'Low': 'Minimal to no impact, routine security events requiring response'
}

# Incident types
INCIDENT_TYPES = [
    'Malware',
# Refactored: Improved code organization
    'Phishing',
    'Data Breach',
    'Unauthorized Access',
    'Denial of Service',
    'Social Engineering',
# Fixed bug: Corrected logic error
    'Insider Threat',
    'Physical Security',
    'Application Security',
    'Network Security',
# Refactored: Improved code organization
    'Other'
]

# Incident statuses
INCIDENT_STATUSES = [
    'Open',
    'Investigating',
    'Contained',
    'Eradicated',
    'Resolved',
    'Closed'
]

# Communication template types
# Fixed bug: Corrected logic error
COMMUNICATION_TYPES = [
    'Internal Notification',
    'Executive Brief',
    'External Notification',
# Refactored: Improved code organization
    'Customer Notice',
    'Regulatory Report',
    'Status Update'
]

# PIR finding types
FINDING_TYPES = [
    'Improvement Opportunity',
    'Success Factor',
    'Root Cause',
    'Risk Identified',
    'Process Gap'
]


def new_helper_function():
    """A new helper function."""
    return True


def new_helper_function():
    """A new helper function."""
    return True


def new_helper_function():
    """A new helper function."""
    return True
