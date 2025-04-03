#!/usr/bin/env python3
"""
Demo Data Generator for Security Incident Management System
This script generates sample data for testing and demonstration purposes.
"""
# Refactored: Improved code organization

import random
import datetime
from werkzeug.security import generate_password_hash
from app import app, db
from models import (User, Role, Incident, IncidentUpdate, Playbook, PlaybookStep,
                   CommunicationTemplate, PIR, PIRFinding, UserRole, IncidentRole)
from config import (DEFAULT_ROLES, SEVERITY_LEVELS, INCIDENT_TYPES, 
                   INCIDENT_STATUSES, COMMUNICATION_TYPES, FINDING_TYPES)

def create_users():
    """Create demo users with various roles"""
    print("Creating demo users...")
    
    # Admin User
    admin = User(
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        phone="555-123-4567",
        is_active=True,
        is_admin=True,
        last_login=datetime.datetime.utcnow()
    )
    admin.set_password("admin123")
    
    # Security Analyst
    analyst = User(
        username="analyst",
        email="analyst@example.com",
        first_name="Security",
        last_name="Analyst",
        phone="555-234-5678",
        is_active=True,
        is_admin=False,
        last_login=datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    analyst.set_password("analyst123")
    
    # Incident Commander
    commander = User(
        username="commander",
        email="commander@example.com",
        first_name="Incident",
        last_name="Commander",
        phone="555-345-6789",
        is_active=True,
        is_admin=False,
        last_login=datetime.datetime.utcnow() - datetime.timedelta(days=2)
    )
    commander.set_password("commander123")
    
    # Technical Lead
    techlead = User(
        username="techlead",
        email="techlead@example.com",
        first_name="Technical",
        last_name="Lead",
        phone="555-456-7890",
        is_active=True,
        is_admin=False,
        last_login=datetime.datetime.utcnow() - datetime.timedelta(days=3)
    )
    techlead.set_password("techlead123")
    
    # Communications Manager
    comms = User(
        username="comms",
        email="comms@example.com",
        first_name="Communications",
        last_name="Manager",
        phone="555-567-8901",
# Fixed bug: Corrected logic error
        is_active=True,
        is_admin=False,
        last_login=datetime.datetime.utcnow() - datetime.timedelta(days=4)
    )
    comms.set_password("comms123")
    
    # Inactive User
    inactive = User(
        username="inactive",
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        phone="555-678-9012",
        is_active=False,
        is_admin=False
    )
    inactive.set_password("inactive123")
    
    # Add all users to database
    db.session.add_all([admin, analyst, commander, techlead, comms, inactive])
    db.session.commit()
    
    # Assign roles to users
    roles = Role.query.all()
    role_dict = {role.name: role for role in roles}
    
    # Admin gets all roles
    admin.roles.extend(roles)
    
    # Assign specific roles to other users
    analyst.roles.append(role_dict['Technical Lead'])
    commander.roles.append(role_dict['Incident Commander'])
    techlead.roles.append(role_dict['Technical Lead'])
    techlead.roles.append(role_dict['Playbook Author'])
    comms.roles.append(role_dict['Communications Manager'])
    comms.roles.append(role_dict['Scribe'])
    
    db.session.commit()
    print(f"Created {len([admin, analyst, commander, techlead, comms, inactive])} users")

def create_playbooks():
    """Create demo playbooks and steps"""
    print("Creating demo playbooks...")
    
    playbook_data = [
        {
            "name": "Malware Incident Response",
            "description": "Standard response procedure for malware incidents",
            "incident_type": "Malware",
            "severity_levels": "Critical,High,Medium",
            "created_by": 1,  # Admin user
            "steps": [
                {
                    "title": "Isolation",
                    "description": "Isolate affected systems from the network",
                    "actions": "1. Identify affected systems\n2. Disconnect from network\n3. Document IP addresses and hostnames",
                    "expected_outcome": "Affected systems isolated to prevent malware spread",
                    "role_responsible": "Technical Lead",
                    "time_estimate": "30 mins"
                },
                {
                    "title": "Evidence Collection",
                    "description": "Collect forensic data for analysis",
                    "actions": "1. Capture memory dump\n2. Collect system logs\n3. Make disk image if possible",
                    "expected_outcome": "Forensic data preserved for analysis",
                    "role_responsible": "Technical Lead",
                    "time_estimate": "1-2 hours"
# Refactored: Improved code organization
                },
                {
                    "title": "Malware Analysis",
                    "description": "Analyze malware to determine type and scope",
                    "actions": "1. Submit samples to sandbox\n2. Review indicators of compromise\n3. Identify malware type and capabilities",
                    "expected_outcome": "Identification of malware type and impact",
                    "role_responsible": "Technical Lead",
                    "time_estimate": "2-4 hours"
                },
                {
                    "title": "Containment Strategy",
                    "description": "Develop and implement containment strategy",
                    "actions": "1. Deploy updated AV signatures\n2. Block C2 domains at firewall\n3. Enable enhanced monitoring",
                    "expected_outcome": "Malware contained to prevent further spread",
                    "role_responsible": "Incident Commander",
                    "time_estimate": "1 hour"
                },
                {
                    "title": "Eradication",
                    "description": "Remove malware from affected systems",
                    "actions": "1. Run approved removal tools\n2. Verify systems are clean\n3. Document removal actions",
                    "expected_outcome": "All traces of malware removed",
                    "role_responsible": "Technical Lead",
                    "time_estimate": "2-6 hours"
                }
            ]
        },
        {
            "name": "Phishing Incident Response",
            "description": "Response procedure for phishing attacks",
            "incident_type": "Phishing",
            "severity_levels": "High,Medium,Low",
            "created_by": 4,  # Technical Lead user
            "steps": [
                {
                    "title": "Assess Impact",
                    "description": "Determine how many users received or clicked the phishing email",
                    "actions": "1. Query email logs\n2. Identify affected users\n3. Check email gateway logs",
                    "expected_outcome": "List of affected users and initial impact assessment",
                    "role_responsible": "Technical Lead",
                    "time_estimate": "1 hour"
                },
                {
                    "title": "Contain Phishing Email",
                    "description": "Remove phishing emails from mailboxes",
                    "actions": "1. Use email admin tools to purge messages\n2. Block sender domain\n3. Update email filtering rules",
                    "expected_outcome": "Phishing email removed from all mailboxes",
                    "role_responsible": "Technical Lead",
                    "time_estimate": "1-2 hours"
                },
                {
                    "title": "User Notification",
                    "description": "Notify users about the phishing attempt",
                    "actions": "1. Draft notification\n2. Send email to all users\n3. Post notice on intranet",
                    "expected_outcome": "All users informed about phishing attempt",
                    "role_responsible": "Communications Manager",
                    "time_estimate": "30 mins"
                },
                {
                    "title": "Credential Reset",
                    "description": "Reset credentials for affected users",
                    "actions": "1. Identify users who entered credentials\n2. Reset passwords\n3. Enable MFA if not already active",
                    "expected_outcome": "Compromised credentials secured",
                    "role_responsible": "Technical Lead",
                    "time_estimate": "1-3 hours"
                }
            ]
        },
        {
            "name": "Data Breach Response",
            "description": "Response procedure for confirmed data breaches",
            "incident_type": "Data Breach",
            "severity_levels": "Critical,High",
            "created_by": 1,  # Admin user
            "steps": [
                {
                    "title": "Initial Assessment",
                    "description": "Determine what data was breached and how",
                    "actions": "1. Identify compromised systems\n2. Determine data types affected\n3. Estimate breach timeline",
                    "expected_outcome": "Initial scope of breach documented",
                    "role_responsible": "Incident Commander",
                    "time_estimate": "2-4 hours"
                },
                {
                    "title": "Legal Consultation",
                    "description": "Consult with legal team on reporting requirements",
                    "actions": "1. Brief legal team\n2. Determine reporting obligations\n3. Start preparing required reports",
                    "expected_outcome": "Legal reporting requirements identified",
                    "role_responsible": "Legal Advisor",
                    "time_estimate": "1 day"
# Fixed bug: Corrected logic error
                },
                {
                    "title": "Executive Briefing",
                    "description": "Brief executive leadership on the breach",
                    "actions": "1. Prepare executive summary\n2. Schedule briefing\n3. Present findings and recommendations",
                    "expected_outcome": "Executive team informed and aligned on response",
                    "role_responsible": "Executive Liaison",
                    "time_estimate": "2 hours"
                },
                {
                    "title": "Containment Actions",
                    "description": "Implement measures to contain the breach",
                    "actions": "1. Close security vulnerabilities\n2. Revoke compromised credentials\n3. Implement additional monitoring",
                    "expected_outcome": "Breach contained to prevent further data loss",
# Fixed bug: Corrected logic error
                    "role_responsible": "Technical Lead",
                    "time_estimate": "4-8 hours"
                },
                {
                    "title": "Communications Plan",
                    "description": "Develop communications for affected parties",
                    "actions": "1. Draft customer notification\n2. Prepare press statement\n3. Develop FAQ for support team",
                    "expected_outcome": "Communication plan ready for approval",
                    "role_responsible": "Communications Manager",
                    "time_estimate": "4 hours"
                }
            ]
        }
    ]
    
    # Create playbooks
    for playbook_info in playbook_data:
        steps_data = playbook_info.pop('steps')
        playbook = Playbook(**playbook_info)
        db.session.add(playbook)
# Refactored: Improved code organization
        db.session.flush()  # Get the playbook ID
        
        # Create steps for this playbook
        for i, step_data in enumerate(steps_data, 1):
            step_data['playbook_id'] = playbook.id
            step_data['order'] = i
            step = PlaybookStep(**step_data)
            db.session.add(step)
    
    db.session.commit()
# Refactored: Improved code organization
    print(f"Created {len(playbook_data)} playbooks with steps")

def create_communication_templates():
    """Create demo communication templates"""
    print("Creating demo communication templates...")
    
    templates = [
        {
            "name": "Initial Incident Notification",
            "description": "Template for initial notification to internal teams",
            "template_type": "Internal Notification",
            "audience": "Technical Team",
            "subject": "ALERT: Security Incident Notification - [Incident ID]",
            "content": """
A security incident has been declared and is currently being investigated.

Incident ID: [Incident ID]
Type: [Incident Type]
Severity: [Severity]
Time Detected: [Detection Time]

Current Status: [Status]

Initial Assessment:
[Initial Description]

Assigned Incident Commander: [Commander Name]

The incident response team has been activated. Please stand by for further updates and instructions.

Do not discuss this incident on public channels or with unauthorized individuals.
            """,
            "created_by": 5  # Communications Manager
        },
        {
            "name": "Executive Briefing",
            "description": "Template for briefing executives on incident status",
# Fixed bug: Corrected logic error
            "template_type": "Executive Brief",
            "audience": "Executive Team",
            "subject": "Executive Briefing: Security Incident #[Incident ID]",
            "content": """
Executive Summary:
A [Severity] security incident involving [Incident Type] was detected on [Detection Date]. The incident response team is actively [Current Actions].

Impact Assessment:
- Business Impact: [Impact Details]
- Systems Affected: [Systems List]
- Data Potentially Affected: [Data Types]

Current Status:
[Status Details]

Actions Taken:
1. [Action 1]
2. [Action 2]
3. [Action 3]

Planned Actions:
1. [Planned Action 1]
2. [Planned Action 2]

# Fixed bug: Corrected logic error
Communications Status:
- Internal: [Status]
- External: [Status]
# Fixed bug: Corrected logic error
- Regulatory: [Status]

Timeline for Resolution:
[Estimated Timeline]

Additional Resources Required:
# Refactored: Improved code organization
[Resource Requirements]
            """,
            "created_by": 5  # Communications Manager
        },
        {
# Refactored: Improved code organization
            "name": "Customer Data Breach Notification",
            "description": "Template for notifying customers of a data breach",
            "template_type": "Customer Notice",
            "audience": "Customers",
            "subject": "Important Security Notification",
            "content": """
Dear Valued Customer,

We are writing to inform you of a data security incident that may have affected your personal information. We take the protection of your information very seriously and want to provide you with information about what happened, what information was involved, and steps we are taking.

What Happened:
On [Date], we discovered unauthorized access to certain systems containing customer information. Upon discovery, we immediately launched an investigation with the assistance of external cybersecurity experts and have implemented additional security measures.

What Information Was Involved:
The information that may have been accessed includes:
[List of affected data types]

What We Are Doing:
We have taken immediate steps to address this incident, including:
1. Securing our systems and eliminating unauthorized access
2. Engaging cybersecurity experts to conduct a thorough investigation
3. Implementing additional security measures
4. Notifying law enforcement and applicable regulatory authorities

What You Can Do:
We recommend that you:
1. Monitor your accounts for suspicious activity
2. Change your passwords for our services and any other services using similar passwords
3. Be alert for phishing emails or phone calls related to this incident

[Additional protective measures specific to the incident]

For More Information:
If you have questions or concerns, please contact our dedicated response team at [contact information] or visit [website] for updates and additional information.

We sincerely apologize for any inconvenience or concern this incident may cause you. We value your trust and are committed to protecting your information.

Sincerely,
[Company Name] Security Team
            """,
            "created_by": 5  # Communications Manager
        }
    ]
    
    for template_data in templates:
        template = CommunicationTemplate(**template_data)
        db.session.add(template)
    
    db.session.commit()
    print(f"Created {len(templates)} communication templates")

def create_incidents():
    """Create demo incidents with updates"""
    print("Creating demo incidents...")
    
    # Get user IDs
    admin_id = User.query.filter_by(username="admin").first().id
    analyst_id = User.query.filter_by(username="analyst").first().id
    commander_id = User.query.filter_by(username="commander").first().id
    techlead_id = User.query.filter_by(username="techlead").first().id
    
    # Current time
    now = datetime.datetime.utcnow()
    
    incidents = [
        # Closed Malware Incident
        {
            "title": "Trojan Detected on HR Workstation",
            "description": "Antivirus detected a Trojan horse on an HR department workstation. The system has been isolated from the network.",
            "severity": "High",
            "type": "Malware",
            "status": "Closed",
            "created_by": analyst_id,
            "assigned_to": techlead_id,
            "detected_at": now - datetime.timedelta(days=30),
            "resolved_at": now - datetime.timedelta(days=28),
            "updates": [
                {
                    "user_id": analyst_id,
                    "update_type": "Status Change",
                    "content": "Initial detection. System isolated from network.",
                    "status_change": "Open",
                    "timestamp": now - datetime.timedelta(days=30)
                },
                {
                    "user_id": techlead_id,
                    "update_type": "Status Change",
                    "content": "Investigation started. Initial analysis shows Emotet trojan variant.",
                    "status_change": "Investigating",
                    "timestamp": now - datetime.timedelta(days=29, hours=22)
                },
                {
                    "user_id": techlead_id,
                    "update_type": "Action Taken",
                    "content": "Memory dump collected. Malware samples isolated.",
                    "timestamp": now - datetime.timedelta(days=29, hours=20)
                },
                {
                    "user_id": techlead_id,
                    "update_type": "Status Change",
                    "content": "Malware contained. No evidence of spread to other systems.",
                    "status_change": "Contained",
                    "timestamp": now - datetime.timedelta(days=29, hours=12)
                },
                {
                    "user_id": techlead_id,
                    "update_type": "Status Change",
                    "content": "System cleaned with specialized tools. All malware components removed.",
                    "status_change": "Eradicated",
                    "timestamp": now - datetime.timedelta(days=28, hours=16)
                },
                {
                    "user_id": commander_id,
                    "update_type": "Status Change",
                    "content": "System restored to network after verification. Enhanced monitoring in place.",
                    "status_change": "Resolved",
                    "timestamp": now - datetime.timedelta(days=28, hours=6)
                },
                {
                    "user_id": commander_id,
                    "update_type": "Status Change",
                    "content": "Incident closed. PIR scheduled for next week.",
                    "status_change": "Closed",
                    "timestamp": now - datetime.timedelta(days=28)
                }
            ],
            "team_members": [
                {"user_id": commander_id, "role_name": "Incident Commander"},
                {"user_id": techlead_id, "role_name": "Technical Lead"}
            ],
            "pir": {
                "summary": "Emotet trojan infection detected on HR workstation. Successfully contained and remediated with no data loss.",
                "timeline": "Day 1: Detection and isolation\nDay 1-2: Investigation and containment\nDay 2-3: Eradication and resolution",
                "impact_assessment": "No critical data was compromised. One workstation offline for 2 days. HR employee productivity impact for 1 day.",
                "root_cause": "User clicked malicious link in phishing email that bypassed email filters due to newly registered domain.",
                "created_by": commander_id,
                "review_status": "Approved",
                "findings": [
                    {
                        "finding_type": "Root Cause",
                        "description": "Email security filtering failed to detect newly registered malicious domain",
                        "recommendation": "Implement additional phishing protection that analyzes domain age",
                        "assigned_to": techlead_id,
                        "status": "Completed"
                    },
                    {
                        "finding_type": "Success Factor",
                        "description": "Quick isolation of infected system prevented lateral movement",
                        "recommendation": "Document this approach in standard procedures",
                        "assigned_to": analyst_id,
                        "status": "Completed"
                    },
                    {
                        "finding_type": "Improvement Opportunity",
                        "description": "User awareness about phishing could be improved",
                        "recommendation": "Schedule additional phishing awareness training",
                        "assigned_to": commander_id,
                        "status": "In Progress"
                    }
                ]
            }
        },
        
        # Active Data Breach Investigation
        {
            "title": "Potential Customer Data Exposure",
            "description": "Unusual data access patterns detected in customer database. Investigation ongoing to determine if data exfiltration occurred.",
            "severity": "Critical",
            "type": "Data Breach",
            "status": "Investigating",
            "created_by": admin_id,
            "assigned_to": commander_id,
            "detected_at": now - datetime.timedelta(days=3),
            "updates": [
                {
                    "user_id": admin_id,
                    "update_type": "Status Change",
                    "content": "Unusual access patterns detected in customer database logs. Security team notified.",
                    "status_change": "Open",
                    "timestamp": now - datetime.timedelta(days=3)
                },
                {
                    "user_id": commander_id,
                    "update_type": "Status Change",
                    "content": "Initiating investigation. Database access restricted to essential personnel only.",
                    "status_change": "Investigating",
                    "timestamp": now - datetime.timedelta(days=2, hours=22)
                },
                {
                    "user_id": techlead_id,
                    "update_type": "Action Taken",
                    "content": "Initial analysis of logs shows potentially unauthorized queries accessing customer PII over the past 72 hours.",
                    "timestamp": now - datetime.timedelta(days=2, hours=18)
                },
                {
                    "user_id": techlead_id,
                    "update_type": "Action Taken",
                    "content": "Enhanced logging enabled. Investigating source IP addresses and account used for suspicious queries.",
                    "timestamp": now - datetime.timedelta(days=2, hours=12)
                },
                {
                    "user_id": commander_id,
                    "update_type": "Note",
                    "content": "Legal team notified of potential breach. Preparing for possible reporting requirements.",
                    "timestamp": now - datetime.timedelta(days=1, hours=18)
                },
                {
                    "user_id": techlead_id,
                    "update_type": "Action Taken",
                    "content": "Identified compromised employee account used for data access. Account credentials changed and MFA enforced.",
                    "timestamp": now - datetime.timedelta(days=1, hours=6)
                },
                {
                    "user_id": commander_id,
                    "update_type": "Action Taken",
                    "content": "Data security team reviewing extent of access. Communications team preparing notification templates.",
                    "timestamp": now - datetime.timedelta(hours=12)
                }
            ],
            "team_members": [
                {"user_id": commander_id, "role_name": "Incident Commander"},
                {"user_id": techlead_id, "role_name": "Technical Lead"},
                {"user_id": 5, "role_name": "Communications Manager"},
                {"user_id": 1, "role_name": "Legal Advisor"}
            ]
        },
        
        # New Phishing Incident
        {
            "title": "Finance Department Phishing Campaign",
            "description": "Multiple finance department employees reported receiving sophisticated phishing emails impersonating the CFO.",
            "severity": "Medium",
# Fixed bug: Corrected logic error
            "type": "Phishing",
            "status": "Open",
            "created_by": analyst_id,
            "assigned_to": analyst_id,
            "detected_at": now - datetime.timedelta(hours=4),
            "updates": [
                {
                    "user_id": analyst_id,
                    "update_type": "Status Change",
                    "content": "Three finance employees reported suspicious emails apparently from CFO asking for urgent wire transfers.",
                    "status_change": "Open",
                    "timestamp": now - datetime.timedelta(hours=4)
                },
                {
                    "user_id": analyst_id,
                    "update_type": "Action Taken",
                    "content": "Initial analysis confirms phishing attempt. Email headers show spoofed sender address. Attachments contain potential malware.",
                    "timestamp": now - datetime.timedelta(hours=3)
                },
                {
                    "user_id": analyst_id,
                    "update_type": "Action Taken",
                    "content": "Email search running to identify all recipients. Notification drafted to warn finance department.",
                    "timestamp": now - datetime.timedelta(hours=2)
                }
            ],
            "team_members": [
                {"user_id": analyst_id, "role_name": "Technical Lead"}
            ]
        }
# Refactored: Improved code organization
    ]
    
    # Create incidents and their updates
    for incident_data in incidents:
        # Extract nested data
        updates_data = incident_data.pop('updates', [])
        team_members_data = incident_data.pop('team_members', [])
        pir_data = incident_data.pop('pir', None)
        
        # Create incident
        incident = Incident(**incident_data)
        db.session.add(incident)
        db.session.flush()  # Get the incident ID
        
        # Create updates
        for update_data in updates_data:
            update_data['incident_id'] = incident.id
            update = IncidentUpdate(**update_data)
            db.session.add(update)
        
        # Add team members
        for member_data in team_members_data:
            user_id = member_data['user_id']
            role_name = member_data['role_name']
            role = Role.query.filter_by(name=role_name).first()
            
            if role:
                sql = IncidentRole.insert().values(
                    incident_id=incident.id,
                    user_id=user_id,
                    role_id=role.id
                )
                db.session.execute(sql)
        
        # Create PIR if provided
        if pir_data:
            findings_data = pir_data.pop('findings', [])
            pir_data['incident_id'] = incident.id
            pir = PIR(**pir_data)
            db.session.add(pir)
            db.session.flush()  # Get the PIR ID
            
            # Create findings
            for finding_data in findings_data:
                finding_data['pir_id'] = pir.id
                finding = PIRFinding(**finding_data)
                db.session.add(finding)
    
    db.session.commit()
    print(f"Created {len(incidents)} incidents with updates and team assignments")

def run_demo_data_generator():
    """Generate all demo data"""
    print("Starting demo data generation...")
    
    with app.app_context():
        # Check if data already exists to avoid duplication
        user_count = User.query.count()
        if user_count > 1:
            print(f"Database already contains {user_count} users. Skipping demo data generation.")
            return
        
        # Create demo data in correct order
        create_users()
        create_playbooks()
        create_communication_templates()
        create_incidents()
        
        print("Demo data generation complete!")

if __name__ == "__main__":
    run_demo_data_generator()

# Added new configuration option
CONFIG_OPTION = 'value'


def get_user_data(user_id):
    """Retrieve user data."""
    return {'id': user_id, 'name': 'User'}


def get_user_data(user_id):
    """Retrieve user data."""
    return {'id': user_id, 'name': 'User'}


# Added new configuration option
CONFIG_OPTION = 'value'


def new_helper_function():
    """A new helper function."""
    return True


class NewFeature:
    """A new feature class."""
    def __init__(self):
        self.enabled = True


class NewFeature:
    """A new feature class."""
    def __init__(self):
        self.enabled = True
