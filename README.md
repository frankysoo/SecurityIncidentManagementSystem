# Security Incident Management System (SecIMS)

![Security Incident Management System](attached_assets/generated-icon.png)

## Overview

SecIMS is a comprehensive platform for tracking, responding to, and analyzing security incidents across your organization. This web-based application provides security teams with the tools they need to effectively manage the entire incident response lifecycle, from initial detection to post-incident review.

## Features

### Incident Management
- **Centralized incident tracking**: Maintain a single source of truth for all security incidents
- **Customizable incident classification**: Categorize incidents by type, severity, and status
- **Timeline-based incident updates**: Document all actions taken during incident response
- **Database indexing**: Optimized database queries for faster incident retrieval

### Team Coordination
- **Role-based access control**: Assign specific roles to team members for each incident
- **Team management**: Track who is responsible for what during an incident
- **Communication tools**: Facilitate effective communication between team members
- **Enhanced security**: CSRF protection for all forms and API endpoints

### Playbooks
- **Standardized response procedures**: Create and maintain playbooks for different incident types
- **Step-by-step guidance**: Follow predefined steps to ensure consistent incident handling
- **Role assignments**: Clearly define responsibilities for each step in the playbook
- **API rate limiting**: Prevent abuse of playbook API endpoints

### Post-Incident Analysis
- **Post-Incident Reviews (PIRs)**: Document lessons learned and improvement opportunities
- **Findings tracking**: Record and track action items from incident reviews
- **Metrics and reporting**: Generate insights from incident data to improve future responses
- **Timezone-aware timestamps**: Accurate timing information for global teams

### User Experience
- **Dark/Light mode**: Toggle between dark and light themes based on user preference
- **Responsive design**: Works on desktop and mobile devices
- **Password policy enforcement**: Ensures strong passwords for all users
- **Standardized messaging**: Create templates for different communication needs

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: SQLAlchemy ORM with SQLite (configurable for other databases)
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Authentication**: Flask-Login for user authentication and session management
- **Security**: Flask-WTF for CSRF protection and custom rate limiting
- **Visualization**: Chart.js for metrics and dashboard visualizations
- **UI**: Dark/Light mode toggle with theme persistence

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/security-incident-management.git
   cd security-incident-management
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

4. Access the application:
   Open your browser and navigate to `http://localhost:5000`

## Initial Setup

When you first run the application, you'll need to:

1. Register an initial admin user at `/register`
2. Log in with your new admin credentials
3. Optionally generate demo data by visiting `/generate-demo-data` (admin only)

### Demo Accounts

If you generate demo data, the following accounts will be created:

- **Admin**: Username: `admin`, Password: `admin123`
- **Security Analyst**: Username: `analyst`, Password: `analyst123`
- **Incident Commander**: Username: `commander`, Password: `commander123`

## Configuration

The application can be configured through environment variables:

- `DATABASE_URL`: Database connection string (default: `sqlite:///sims.db`)
- `SESSION_SECRET`: Secret key for session management (default: `dev-secret-key`)
- `FLASK_ENV`: Set to `production` for production environment settings

In production mode, the following security enhancements are automatically applied:
- Secure session cookies
- HTTP-only cookies
- SameSite cookie policy
- Random session key generation if not provided

## Project Structure

```
security-incident-management/
├── app.py                  # Application initialization
├── config.py               # Configuration settings
├── demo_data_generator.py  # Script to generate sample data
├── helpers.py              # Helper functions
├── main.py                 # Application entry point
├── models.py               # Database models
├── routes.py               # Route definitions
├── static/                 # Static assets
│   ├── css/                # CSS stylesheets
│   └── js/                 # JavaScript files
└── templates/              # HTML templates
    ├── base.html           # Base template
    ├── dashboard.html      # Dashboard template
    ├── incidents/          # Incident-related templates
    ├── playbooks/          # Playbook-related templates
    └── ...                 # Other templates
```

## Development

### Running in Debug Mode

For development purposes, the application runs in debug mode by default:

```bash
python main.py
```

### Database Migrations

The application automatically creates the necessary database tables on startup.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NIST SP 800-61 for incident response guidance
- ISO 27035 for incident management best practices
