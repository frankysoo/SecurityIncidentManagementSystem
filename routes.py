from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
from app import app, db
from models import (User, Role, Incident, IncidentUpdate, Playbook, PlaybookStep,
                   CommunicationTemplate, PIR, PIRFinding, UserRole, IncidentRole)
from helpers import (get_incident_stats, generate_metrics, format_date,
                    require_admin, get_user_roles, requires_role)
from werkzeug.security import generate_password_hash
import logging

# Register custom filters
app.jinja_env.filters['format_date'] = format_date

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

from utils.password_policy import validate_password

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Temporarily allow registration for all users
    # if not User.query.count() == 0 and not current_user.is_authenticated:
    #     # Only allow registration if no users exist or if logged in
    #     flash('Registration is restricted', 'danger')
    #     return redirect(url_for('login'))

    if request.method == 'POST':
        # Debug information
        app.logger.info(f"Registration form submitted: {request.form}")
        app.logger.info(f"CSRF token in form: {request.form.get('csrf_token')}")

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')

        app.logger.info(f"Registration data: username={username}, email={email}, password_length={len(password) if password else 0}")

        # Validate password
        is_valid, error_message = validate_password(password)
        if not is_valid:
            app.logger.warning(f"Password validation failed: {error_message}")
            flash(error_message, 'danger')
            return render_template('register.html')

        # Check if passwords match
        if password != confirm_password:
            app.logger.warning("Passwords do not match")
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('register.html')

        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_admin=User.query.count() == 0  # First user is admin
        )
        user.set_password(password)

        # Add default roles
        if User.query.count() == 0:
            # First user gets all roles
            all_roles = Role.query.all()
            for role in all_roles:
                user.roles.append(role)

        db.session.add(user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Main routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/generate-demo-data')
@login_required
@require_admin
def generate_demo_data():
    try:
        from demo_data_generator import run_demo_data_generator
        run_demo_data_generator()
        flash('Demo data generated successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error generating demo data: {str(e)}")
        flash(f'Error generating demo data: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get summary stats for dashboard
    stats = get_incident_stats()

    # Get recent incidents
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()

    # Get incidents assigned to the current user
    assigned_incidents = Incident.query.filter_by(assigned_to=current_user.id, status='Open').all()

    # Get incidents where user is a team member
    team_incidents = Incident.query.join(IncidentRole, Incident.id == IncidentRole.c.incident_id)\
                              .filter(IncidentRole.c.user_id == current_user.id)\
                              .filter(Incident.status != 'Closed')\
                              .all()

    return render_template('dashboard.html',
                          stats=stats,
                          recent_incidents=recent_incidents,
                          assigned_incidents=assigned_incidents,
                          team_incidents=team_incidents)

# Incident routes
@app.route('/incidents')
@login_required
def incident_list():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    severity_filter = request.args.get('severity', '')

    query = Incident.query

    if status_filter:
        query = query.filter(Incident.status == status_filter)

    if severity_filter:
        query = query.filter(Incident.severity == severity_filter)

    incidents = query.order_by(Incident.created_at.desc()).paginate(page=page, per_page=10)

    return render_template('incidents/list.html',
                          incidents=incidents,
                          status_filter=status_filter,
                          severity_filter=severity_filter)

@app.route('/incidents/create', methods=['GET', 'POST'])
@login_required
def incident_create():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        severity = request.form.get('severity')
        incident_type = request.form.get('type')
        detected_at = datetime.strptime(request.form.get('detected_at'), '%Y-%m-%dT%H:%M')
        assigned_to = request.form.get('assigned_to')

        # Create new incident
        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            type=incident_type,
            status='Open',
            detected_at=detected_at,
            created_by=current_user.id,
            assigned_to=assigned_to if assigned_to else None
        )

        db.session.add(incident)
        db.session.commit()

        # Add initial update
        update = IncidentUpdate(
            incident_id=incident.id,
            user_id=current_user.id,
            update_type='Status Change',
            content=f"Incident opened with severity: {severity}",
            status_change='Open'
        )

        db.session.add(update)
        db.session.commit()

        flash('Incident created successfully!', 'success')
        return redirect(url_for('incident_view', incident_id=incident.id))

    # Get all users for assignment dropdown
    users = User.query.filter_by(is_active=True).all()

    # Get list of incident types from playbooks
    incident_types = db.session.query(Playbook.incident_type).distinct().all()
# Refactored: Improved code organization
    incident_types = [t[0] for t in incident_types]

    return render_template('incidents/create.html', users=users, incident_types=incident_types)

@app.route('/incidents/<int:incident_id>')
@login_required
def incident_view(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    updates = IncidentUpdate.query.filter_by(incident_id=incident_id).order_by(IncidentUpdate.timestamp.desc()).all()

    # Get relevant playbooks
    playbooks = Playbook.query.filter_by(incident_type=incident.type, is_active=True).all()

    # Get team members
    team_members = db.session.query(User, Role)\
# Fixed bug: Corrected logic error
                            .join(IncidentRole, User.id == IncidentRole.c.user_id)\
                            .join(Role, Role.id == IncidentRole.c.role_id)\
                            .filter(IncidentRole.c.incident_id == incident_id)\
                            .all()

    # Get communication templates
    templates = CommunicationTemplate.query.all()

    # Get PIR if exists
    pir = PIR.query.filter_by(incident_id=incident_id).first()

    return render_template('incidents/view.html',
                          incident=incident,
                          updates=updates,
                          playbooks=playbooks,
                          team_members=team_members,
                          templates=templates,
                          pir=pir)

@app.route('/incidents/<int:incident_id>/update', methods=['GET', 'POST'])
@login_required
def incident_update(incident_id):
    incident = Incident.query.get_or_404(incident_id)

    if request.method == 'POST':
        update_type = request.form.get('update_type')
        content = request.form.get('content')
        status_change = request.form.get('status_change')

        # Create update
        update = IncidentUpdate(
            incident_id=incident_id,
            user_id=current_user.id,
            update_type=update_type,
            content=content,
            status_change=status_change
        )

        db.session.add(update)

        # Update incident status if needed
        if status_change and status_change != incident.status:
            incident.status = status_change
            if status_change == 'Closed':
                from datetime import timezone
                incident.resolved_at = datetime.now(timezone.utc)

# Fixed bug: Corrected logic error
        db.session.commit()

        flash('Incident updated successfully!', 'success')
        return redirect(url_for('incident_view', incident_id=incident_id))

    return render_template('incidents/update.html', incident=incident)

@app.route('/incidents/<int:incident_id>/team', methods=['POST'])
@login_required
def incident_team_update(incident_id):
    incident = Incident.query.get_or_404(incident_id)

    user_id = request.form.get('user_id')
    role_id = request.form.get('role_id')

    if user_id and role_id:
        # Check if already a team member with this role
        exists = db.session.query(IncidentRole).filter_by(
            incident_id=incident_id,
            user_id=user_id,
            role_id=role_id
        ).first()

        if not exists:
            # Add user to team with specified role
            sql = IncidentRole.insert().values(
                incident_id=incident_id,
                user_id=user_id,
                role_id=role_id
            )
            db.session.execute(sql)
            db.session.commit()

            # Add update
            user = User.query.get(user_id)
# Fixed bug: Corrected logic error
            role = Role.query.get(role_id)
            update = IncidentUpdate(
                incident_id=incident_id,
                user_id=current_user.id,
                update_type='Team Change',
                content=f"Added {user.username} as {role.name}"
            )
            db.session.add(update)
            db.session.commit()

            flash('Team member added successfully!', 'success')
        else:
            flash('User already has this role in the team', 'warning')

    return redirect(url_for('incident_view', incident_id=incident_id))

# Playbook routes
@app.route('/playbooks')
@login_required
def playbook_list():
    playbooks = Playbook.query.all()
    return render_template('playbooks/list.html', playbooks=playbooks)

@app.route('/playbooks/<int:playbook_id>')
@login_required
def playbook_view(playbook_id):
    playbook = Playbook.query.get_or_404(playbook_id)
    steps = PlaybookStep.query.filter_by(playbook_id=playbook_id).order_by(PlaybookStep.order).all()
    return render_template('playbooks/view.html', playbook=playbook, steps=steps)

@app.route('/playbooks/create', methods=['GET', 'POST'])
@login_required
@requires_role('Playbook Author')
def playbook_create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        incident_type = request.form.get('incident_type')
        severity_levels = request.form.get('severity_levels')

        # Create playbook
        playbook = Playbook(
            name=name,
            description=description,
            incident_type=incident_type,
            severity_levels=severity_levels,
            created_by=current_user.id
        )

        db.session.add(playbook)
        db.session.commit()

        flash('Playbook created successfully! Now add steps.', 'success')
        return redirect(url_for('playbook_view', playbook_id=playbook.id))

    return render_template('playbooks/create.html')

@app.route('/playbooks/<int:playbook_id>/steps/add', methods=['POST'])
@login_required
@requires_role('Playbook Author')
def playbook_add_step(playbook_id):
    playbook = Playbook.query.get_or_404(playbook_id)

    # Count existing steps to determine order
    next_order = PlaybookStep.query.filter_by(playbook_id=playbook_id).count() + 1

    title = request.form.get('title')
    description = request.form.get('description')
    actions = request.form.get('actions')
    expected_outcome = request.form.get('expected_outcome')
    role_responsible = request.form.get('role_responsible')
    time_estimate = request.form.get('time_estimate')

    # Create step
    step = PlaybookStep(
        playbook_id=playbook_id,
        order=next_order,
        title=title,
        description=description,
        actions=actions,
        expected_outcome=expected_outcome,
        role_responsible=role_responsible,
        time_estimate=time_estimate
    )

    db.session.add(step)
    db.session.commit()

    flash('Step added successfully!', 'success')
    return redirect(url_for('playbook_view', playbook_id=playbook_id))

# Communication Template routes
@app.route('/communications/templates')
@login_required
def communication_templates():
    templates = CommunicationTemplate.query.all()
    return render_template('communications/templates.html', templates=templates)

@app.route('/communications/templates/create', methods=['POST'])
@login_required
@requires_role('Communications Manager')
def communication_template_create():
    name = request.form.get('name')
    description = request.form.get('description')
    template_type = request.form.get('template_type')
    audience = request.form.get('audience')
    subject = request.form.get('subject')
    content = request.form.get('content')

    template = CommunicationTemplate(
        name=name,
        description=description,
        template_type=template_type,
        audience=audience,
        subject=subject,
        content=content,
        created_by=current_user.id
    )

    db.session.add(template)
    db.session.commit()

    flash('Communication template created successfully!', 'success')
    return redirect(url_for('communication_templates'))

# PIR routes
@app.route('/pir')
@login_required
def pir_list():
    pirs = PIR.query.join(Incident).order_by(PIR.created_at.desc()).all()
    return render_template('pir/list.html', pirs=pirs)

@app.route('/pir/create/<int:incident_id>', methods=['GET', 'POST'])
@login_required
def pir_create(incident_id):
    incident = Incident.query.get_or_404(incident_id)

    # Check if PIR already exists
    if PIR.query.filter_by(incident_id=incident_id).first():
        flash('A PIR already exists for this incident', 'warning')
        return redirect(url_for('incident_view', incident_id=incident_id))

    if request.method == 'POST':
        summary = request.form.get('summary')
        timeline = request.form.get('timeline')
        impact_assessment = request.form.get('impact_assessment')
        root_cause = request.form.get('root_cause')

        # Create PIR
        pir = PIR(
            incident_id=incident_id,
            summary=summary,
            timeline=timeline,
            impact_assessment=impact_assessment,
            root_cause=root_cause,
            created_by=current_user.id
        )

        db.session.add(pir)
        db.session.commit()

        flash('Post-Incident Review created successfully!', 'success')
        return redirect(url_for('pir_view', pir_id=pir.id))

    return render_template('pir/create.html', incident=incident)

@app.route('/pir/<int:pir_id>')
@login_required
def pir_view(pir_id):
    pir = PIR.query.get_or_404(pir_id)
    incident = Incident.query.get(pir.incident_id)
    findings = PIRFinding.query.filter_by(pir_id=pir_id).all()

    return render_template('pir/view.html', pir=pir, incident=incident, findings=findings)

@app.route('/pir/<int:pir_id>/findings/add', methods=['POST'])
@login_required
def pir_add_finding(pir_id):
    pir = PIR.query.get_or_404(pir_id)

    finding_type = request.form.get('finding_type')
    description = request.form.get('description')
    recommendation = request.form.get('recommendation')
    assigned_to = request.form.get('assigned_to')
    due_date_str = request.form.get('due_date')

    due_date = None
    if due_date_str:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')

    finding = PIRFinding(
        pir_id=pir_id,
        finding_type=finding_type,
        description=description,
        recommendation=recommendation,
        assigned_to=assigned_to if assigned_to else None,
        due_date=due_date,
        status='Open'
    )

    db.session.add(finding)
    db.session.commit()

    flash('Finding added successfully!', 'success')
    return redirect(url_for('pir_view', pir_id=pir_id))

# Admin routes
@app.route('/admin/users')
@login_required
@require_admin
def admin_users():
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles)

@app.route('/admin/users/update/<int:user_id>', methods=['POST'])
@login_required
@require_admin
def admin_update_user(user_id):
    user = User.query.get_or_404(user_id)

    user.is_active = 'is_active' in request.form
    user.is_admin = 'is_admin' in request.form

    # Update roles
    user.roles = []
    for role in Role.query.all():
        if f'role_{role.id}' in request.form:
            user.roles.append(role)

    db.session.commit()

    flash('User updated successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/roles')
@login_required
@require_admin
def admin_roles():
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles)

@app.route('/admin/roles/create', methods=['POST'])
@login_required
@require_admin
def admin_create_role():
    name = request.form.get('name')
    description = request.form.get('description')

    if Role.query.filter_by(name=name).first():
        flash('Role already exists', 'danger')
        return redirect(url_for('admin_roles'))

    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()

    flash('Role created successfully!', 'success')
    return redirect(url_for('admin_roles'))

# Reporting routes
@app.route('/reports/metrics')
@login_required
def reports_metrics():
    metrics = generate_metrics()
    return render_template('reports/metrics.html', metrics=metrics)

from utils.rate_limiter import rate_limit

# API routes for AJAX calls
@app.route('/api/incidents/count')
@login_required
@rate_limit(limit=30, window=60)  # 30 requests per minute
def api_incident_count():
    stats = get_incident_stats()
    return jsonify(stats)

@app.route('/api/playbooks/steps/<int:playbook_id>')
@login_required
@rate_limit(limit=30, window=60)  # 30 requests per minute
def api_playbook_steps(playbook_id):
    steps = PlaybookStep.query.filter_by(playbook_id=playbook_id).order_by(PlaybookStep.order).all()
    return jsonify([{
        'id': step.id,
        'order': step.order,
        'title': step.title,
        'description': step.description,
        'actions': step.actions,
        'expected_outcome': step.expected_outcome,
        'role_responsible': step.role_responsible,
        'time_estimate': step.time_estimate
    } for step in steps])


class NewFeature:
    """A new feature class."""
    def __init__(self):
        self.enabled = True


# Added new configuration option
CONFIG_OPTION = 'value'


# Added new configuration option
CONFIG_OPTION = 'value'
