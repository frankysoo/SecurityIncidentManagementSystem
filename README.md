# Security Incident Management System (SecIMS)

![Security Incident Management System](static/img/logo.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)

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
   git clone https://github.com/frankysoo/SecurityIncidentManagementSystem.git
   cd SecurityIncidentManagementSystem
   ```

2. Create a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

5. Access the application:
   Open your browser and navigate to `http://localhost:5001`

### Docker Installation (Alternative)

1. Build the Docker image:
   ```bash
   docker build -t secims .
   ```

2. Run the container:
   ```bash
   docker run -p 5001:5001 secims
   ```

3. Access the application at `http://localhost:5001`

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
SecurityIncidentManagementSystem/
├── app.py                  # Application initialization
├── config.py               # Configuration settings
├── demo_data_generator.py  # Script to generate sample data
├── helpers.py              # Helper functions
├── main.py                 # Application entry point
├── models.py               # Database models
├── routes.py               # Route definitions
├── utils/                  # Utility modules
│   ├── __init__.py         # Package initialization
│   ├── password_policy.py  # Password validation
│   └── rate_limiter.py     # API rate limiting
├── static/                 # Static assets
│   ├── css/                # CSS stylesheets
│   │   └── custom.css      # Custom styling
│   ├── js/                 # JavaScript files
│   │   ├── dashboard.js    # Dashboard functionality
│   │   ├── main.js         # Main application logic
│   │   └── theme-toggle.js # Dark/light mode toggle
│   └── img/                # Images and icons
└── templates/              # HTML templates
    ├── base.html           # Base template
    ├── layout.html         # Layout template
    ├── dashboard.html      # Dashboard template
    ├── incidents/          # Incident-related templates
    ├── playbooks/          # Playbook-related templates
    ├── pir/                # Post-incident review templates
    ├── communications/     # Communication templates
    └── admin/              # Admin panel templates
```

## Development

### Running in Debug Mode

For development purposes, the application runs in debug mode by default:

```bash
python main.py
```

You can also specify a different port if needed:

```bash
# Edit main.py to change the port
app.run(host="0.0.0.0", port=5001, debug=True)
```

### Database Management

The application automatically creates the necessary database tables on startup. The default database is SQLite, which is stored in the file `sims.db` in the project root directory.

### Security Features

1. **CSRF Protection**: All forms are protected against Cross-Site Request Forgery attacks using Flask-WTF.

2. **Password Policy**: User passwords are validated against a security policy that requires:
   - Minimum length
   - Uppercase and lowercase letters
   - Numbers
   - Special characters

3. **Rate Limiting**: API endpoints are protected against abuse with rate limiting.

4. **Secure Cookies**: In production mode, cookies are set with secure flags.

### Customization

#### Themes
The application supports both light and dark themes. Users can toggle between themes using the theme switch in the navigation bar.

#### Adding New Incident Types
To add new incident types, create new playbooks with the desired incident type. The system will automatically make these types available when creating new incidents.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Write docstrings for all functions and classes
- Include unit tests for new features

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 5001 is already in use, edit `main.py` to use a different port.

2. **Database errors**: If you encounter database errors, try deleting the `sims.db` file and restarting the application to recreate the database schema.

3. **CSRF token errors**: If you get CSRF token errors, make sure all forms include the CSRF token:
   ```html
   <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
   ```

4. **Timezone errors**: If you encounter timezone-related errors, ensure you're using the correct import:
   ```python
   from datetime import datetime, timezone
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NIST SP 800-61 for incident response guidance
- ISO 27035 for incident management best practices
- Bootstrap for the responsive UI framework
- Chart.js for data visualization
- Flask and SQLAlchemy for the backend framework

## Contact

For questions or support, please open an issue on the GitHub repository.


### New Feature
Documented the new feature that was added recently.

### Improvements
- Enhanced user interface
- Optimized database queries

#### Bug Fixes
- Fixed issue with login
- Resolved problem with data display

### New Feature
Documented the new feature that was added recently.

### Improvements
- Enhanced user interface
- Optimized database queries

### Improvements
- Enhanced user interface
- Optimized database queries

### Improvements
- Enhanced user interface
- Optimized database queries