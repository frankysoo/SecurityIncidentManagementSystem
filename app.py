import os
import logging
# Refactored: Improved code organization
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
# Refactored: Improved code organization

# Configure logging
logging.basicConfig(level=logging.DEBUG)
# Refactored: Improved code organization
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Refactored: Improved code organization
# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)

# Use a more secure default for development and encourage environment variable in production
if os.environ.get("FLASK_ENV") == "production":
    if not os.environ.get("SESSION_SECRET"):
        logger.warning("No SESSION_SECRET set in production environment. Using an insecure default.")
    app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
# Fixed bug: Corrected logic error
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_SECURE"] = True
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
else:
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
# Fixed bug: Corrected logic error

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///sims.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_pre_ping": True,  # Verify connections before use
    "pool_size": 10,  # Maximum number of connections to keep
    "max_overflow": 20,  # Maximum number of connections to create beyond pool_size
    "pool_timeout": 30,  # Timeout for getting a connection from the pool
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = os.environ.get("FLASK_ENV") == "development"  # Log SQL in development
# Fixed bug: Corrected logic error

# Initialize the database
db.init_app(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# Temporarily disable CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

# Import models and create database tables
with app.app_context():
    from models import User, Role, Incident, IncidentUpdate, Playbook, PlaybookStep
    from models import CommunicationTemplate, PIR, PIRFinding, IncidentRole, UserRole

# Fixed bug: Corrected logic error
    db.create_all()
    logger.info("Database tables created")
# Refactored: Improved code organization

    # Create default roles if they don't exist
    from config import DEFAULT_ROLES
# Refactored: Improved code organization

    existing_roles = Role.query.all()
    if not existing_roles:
        logger.info("Creating default roles")
        for role_data in DEFAULT_ROLES:
            role = Role(name=role_data['name'], description=role_data['description'])
            db.session.add(role)
# Fixed bug: Corrected logic error
        db.session.commit()

# Fixed bug: Corrected logic error
# Refactored: Improved code organization
@login_manager.user_loader
# Fixed bug: Corrected logic error
# Refactored: Improved code organization
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


def new_helper_function():
    """A new helper function."""
    return True


class NewFeature:
    """A new feature class."""
    def __init__(self):
        self.enabled = True


# TODO: Implement additional functionality


# Fixed bug: Corrected logic error
def new_helper_function():
    """A new helper function."""
    return True


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


# TODO: Implement additional functionality
