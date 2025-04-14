from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import json

from app import app, db
from models import (
    User, Team, TeamMember, Incident, Activity, Comment, 
    Attachment, Playbook, CommunicationTemplate, PIR
)
from utils import (
    requires_role, format_datetime, get_incident_metrics,
    incident_type_options, severity_options, status_options,
    activity_type_options, get_assignable_users
)

# Register template filters
app.jinja_env.filters['format_datetime'] = format_datetime

# ------------------------------------------------------
# Authentication Routes
# ------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.utcnow()
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and not current_user.role == 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validate input
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role='analyst'  # Default role for new users
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# ------------------------------------------------------
# Main Routes
# ------------------------------------------------------

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get counts of incidents by status and severity
    status_counts = db.session.query(
        Incident.status, db.func.count(Incident.id)
    ).group_by(Incident.status).all()
    
    severity_counts = db.session.query(
        Incident.severity, db.func.count(Incident.id)
    ).group_by(Incident.severity).all()
    
    # Get recent incidents
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()
    
    # Get assigned incidents
    assigned_incidents = Incident.query.filter_by(assigned_to=current_user.id).all()
    
    # Get metrics
    metrics = get_incident_metrics()
    
    return render_template(
        'reports/dashboard.html',
        status_counts=dict(status_counts),
        severity_counts=dict(severity_counts),
        recent_incidents=recent_incidents,
        assigned_incidents=assigned_incidents,
        metrics=metrics
    )

# ------------------------------------------------------
# Incident Routes
# ------------------------------------------------------

@app.route('/incidents')
@login_required
def list_incidents():
    # Get filter parameters
    status = request.args.get('status')
    severity = request.args.get('severity')
    incident_type = request.args.get('type')
    
    # Start with base query
    query = Incident.query
    
    # Apply filters if provided
    if status:
        query = query.filter_by(status=status)
    if severity:
        query = query.filter_by(severity=severity)
    if incident_type:
        query = query.filter_by(incident_type=incident_type)
    
    # Get paginated results
    page = request.args.get('page', 1, type=int)
    incidents = query.order_by(Incident.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template(
        'incidents/list.html',
        incidents=incidents,
        status_options=status_options,
        severity_options=severity_options,
        incident_type_options=incident_type_options,
        current_filters={
            'status': status,
            'severity': severity,
            'type': incident_type
        }
    )

@app.route('/incidents/create', methods=['GET', 'POST'])
@login_required
def create_incident():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        severity = request.form.get('severity')
        incident_type = request.form.get('incident_type')
        affected_systems = request.form.get('affected_systems', '').split(',')
        affected_systems = [system.strip() for system in affected_systems if system.strip()]
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        detection_time = request.form.get('detection_time')
        
        # Validate required fields
        if not all([title, severity, incident_type]):
            flash('Please fill in all required fields', 'danger')
            return render_template(
                'incidents/create.html',
                severity_options=severity_options,
                incident_type_options=incident_type_options
            )
        
        # Process detection time if provided
        detection_time_obj = None
        if detection_time:
            try:
                detection_time_obj = datetime.strptime(detection_time, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid detection time format', 'danger')
                return render_template(
                    'incidents/create.html',
                    severity_options=severity_options,
                    incident_type_options=incident_type_options
                )
        
        # Create new incident
        new_incident = Incident(
            title=title,
            description=description,
            severity=severity,
            incident_type=incident_type,
            affected_systems=affected_systems,
            tags=tags,
            created_by=current_user.id,
            detection_time=detection_time_obj,
            status='open'
        )
        
        db.session.add(new_incident)
        db.session.commit()
        
        # Create initial activity record
        activity = Activity(
            incident_id=new_incident.id,
            user_id=current_user.id,
            description=f"Incident created: {title}",
            activity_type="detection"
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Incident created successfully', 'success')
        return redirect(url_for('view_incident', incident_id=new_incident.id))
    
    return render_template(
        'incidents/create.html',
        severity_options=severity_options,
        incident_type_options=incident_type_options
    )

@app.route('/incidents/<int:incident_id>')
@login_required
def view_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    activities = Activity.query.filter_by(incident_id=incident_id).order_by(Activity.created_at).all()
    comments = Comment.query.filter_by(incident_id=incident_id).order_by(Comment.created_at).all()
    
    # Get relevant playbooks for this incident type
    playbooks = Playbook.query.filter_by(incident_type=incident.incident_type).all()
    
    # Get communication templates relevant to this incident type
    templates = CommunicationTemplate.query.filter(
        (CommunicationTemplate.incident_type == incident.incident_type) | 
        (CommunicationTemplate.incident_type.is_(None))
    ).all()
    
    # Get assignable users
    assignable_users = get_assignable_users()
    
    # Get teams
    teams = Team.query.all()
    
    return render_template(
        'incidents/view.html',
        incident=incident,
        activities=activities,
        comments=comments,
        playbooks=playbooks,
        templates=templates,
        assignable_users=assignable_users,
        teams=teams,
        activity_type_options=activity_type_options,
        status_options=status_options
    )

@app.route('/incidents/<int:incident_id>/update', methods=['POST'])
@login_required
def update_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    
    # Get form data
    field = request.form.get('field')
    value = request.form.get('value')
    
    if field and value:
        old_value = getattr(incident, field, None)
        
        # Update the field based on type
        if field == 'assigned_to':
            incident.assigned_to = int(value) if value != 'none' else None
            activity_desc = f"Assigned incident to {User.query.get(int(value)).username if value != 'none' else 'no one'}"
        elif field == 'assigned_team':
            incident.assigned_team = int(value) if value != 'none' else None
            activity_desc = f"Assigned incident to team {Team.query.get(int(value)).name if value != 'none' else 'no team'}"
        elif field == 'status':
            incident.status = value
            activity_desc = f"Updated status from {old_value} to {value}"
            
            # If status changed to resolved, set resolution time
            if value == 'resolved' and old_value != 'resolved':
                incident.resolution_time = datetime.utcnow()
        elif field == 'severity':
            incident.severity = value
            activity_desc = f"Updated severity from {old_value} to {value}"
        elif field == 'resolution':
            incident.resolution = value
            activity_desc = f"Updated resolution notes"
        else:
            # Generic update
            setattr(incident, field, value)
            activity_desc = f"Updated {field} from {old_value} to {value}"
        
        # Update the incident
        incident.updated_at = datetime.utcnow()
        
        # Create activity record
        activity = Activity(
            incident_id=incident.id,
            user_id=current_user.id,
            description=activity_desc,
            activity_type="analysis"  # Default to analysis for updates
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Incident updated'})
    
    return jsonify({'success': False, 'message': 'Invalid request'}), 400

@app.route('/incidents/<int:incident_id>/add_comment', methods=['POST'])
@login_required
def add_comment(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    content = request.form.get('content')
    
    if not content:
        return jsonify({'success': False, 'message': 'Comment cannot be empty'}), 400
    
    comment = Comment(
        incident_id=incident_id,
        user_id=current_user.id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.get_full_name(),
            'created_at': format_datetime(comment.created_at)
        }
    })

@app.route('/incidents/<int:incident_id>/add_activity', methods=['POST'])
@login_required
def add_activity(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    description = request.form.get('description')
    activity_type = request.form.get('activity_type')
    
    if not description or not activity_type:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    activity = Activity(
        incident_id=incident_id,
        user_id=current_user.id,
        description=description,
        activity_type=activity_type
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'activity': {
            'id': activity.id,
            'description': activity.description,
            'activity_type': activity.activity_type,
            'user': activity.user.get_full_name(),
            'created_at': format_datetime(activity.created_at)
        }
    })

# ------------------------------------------------------
# Playbook Routes
# ------------------------------------------------------

@app.route('/playbooks')
@login_required
def list_playbooks():
    incident_type = request.args.get('type')
    
    # Base query
    query = Playbook.query
    
    # Apply filter if provided
    if incident_type:
        query = query.filter_by(incident_type=incident_type)
    
    # Get paginated results
    page = request.args.get('page', 1, type=int)
    playbooks = query.order_by(Playbook.title).paginate(page=page, per_page=10)
    
    return render_template(
        'playbooks/list.html',
        playbooks=playbooks,
        incident_type_options=incident_type_options,
        current_filters={
            'type': incident_type
        }
    )

@app.route('/playbooks/create', methods=['GET', 'POST'])
@login_required
@requires_role(['admin', 'manager'])
def create_playbook():
    if request.method == 'POST':
        title = request.form.get('title')
        incident_type = request.form.get('incident_type')
        description = request.form.get('description')
        steps_json = request.form.get('steps')
        
        # Validate required fields
        if not all([title, incident_type]):
            flash('Please fill in all required fields', 'danger')
            return render_template(
                'playbooks/create.html',
                incident_type_options=incident_type_options
            )
        
        # Parse steps JSON
        try:
            steps = json.loads(steps_json)
        except json.JSONDecodeError:
            flash('Invalid steps format', 'danger')
            return render_template(
                'playbooks/create.html',
                incident_type_options=incident_type_options
            )
        
        # Create new playbook
        playbook = Playbook(
            title=title,
            incident_type=incident_type,
            description=description,
            steps=steps,
            created_by=current_user.id
        )
        
        db.session.add(playbook)
        db.session.commit()
        
        flash('Playbook created successfully', 'success')
        return redirect(url_for('view_playbook', playbook_id=playbook.id))
    
    return render_template(
        'playbooks/create.html',
        incident_type_options=incident_type_options
    )

@app.route('/playbooks/<int:playbook_id>')
@login_required
def view_playbook(playbook_id):
    playbook = Playbook.query.get_or_404(playbook_id)
    return render_template('playbooks/view.html', playbook=playbook)

# ------------------------------------------------------
# Team Routes
# ------------------------------------------------------

@app.route('/teams')
@login_required
def list_teams():
    teams = Team.query.all()
    return render_template('teams/list.html', teams=teams)

@app.route('/teams/create', methods=['GET', 'POST'])
@login_required
@requires_role(['admin', 'manager'])
def create_team():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Team name is required', 'danger')
            return render_template('teams/create.html')
        
        # Create new team
        team = Team(
            name=name,
            description=description
        )
        
        db.session.add(team)
        db.session.commit()
        
        flash('Team created successfully', 'success')
        return redirect(url_for('view_team', team_id=team.id))
    
    return render_template('teams/create.html')

@app.route('/teams/<int:team_id>')
@login_required
def view_team(team_id):
    team = Team.query.get_or_404(team_id)
    members = TeamMember.query.filter_by(team_id=team_id).all()
    users = User.query.all()
    
    return render_template(
        'teams/view.html',
        team=team,
        members=members,
        users=users
    )

@app.route('/teams/<int:team_id>/add_member', methods=['POST'])
@login_required
@requires_role(['admin', 'manager'])
def add_team_member(team_id):
    team = Team.query.get_or_404(team_id)
    user_id = request.form.get('user_id')
    role = request.form.get('role')
    
    if not user_id or not role:
        flash('User and role are required', 'danger')
        return redirect(url_for('view_team', team_id=team_id))
    
    # Check if user is already a member
    existing_member = TeamMember.query.filter_by(
        team_id=team_id, user_id=user_id
    ).first()
    
    if existing_member:
        flash('User is already a member of this team', 'warning')
        return redirect(url_for('view_team', team_id=team_id))
    
    # Add member
    member = TeamMember(
        team_id=team_id,
        user_id=user_id,
        role=role
    )
    
    db.session.add(member)
    db.session.commit()
    
    flash('Member added to team', 'success')
    return redirect(url_for('view_team', team_id=team_id))

@app.route('/teams/<int:team_id>/remove_member/<int:member_id>', methods=['POST'])
@login_required
@requires_role(['admin', 'manager'])
def remove_team_member(team_id, member_id):
    member = TeamMember.query.get_or_404(member_id)
    
    # Ensure member belongs to the specified team
    if member.team_id != team_id:
        abort(404)
    
    db.session.delete(member)
    db.session.commit()
    
    flash('Member removed from team', 'success')
    return redirect(url_for('view_team', team_id=team_id))

# ------------------------------------------------------
# Communication Template Routes
# ------------------------------------------------------

@app.route('/communications/templates')
@login_required
def list_communication_templates():
    template_type = request.args.get('type')
    incident_type = request.args.get('incident_type')
    
    # Base query
    query = CommunicationTemplate.query
    
    # Apply filters if provided
    if template_type:
        query = query.filter_by(template_type=template_type)
    if incident_type:
        query = query.filter_by(incident_type=incident_type)
    
    templates = query.order_by(CommunicationTemplate.name).all()
    
    template_type_options = ['internal', 'external', 'executive', 'customer']
    
    return render_template(
        'communications/templates.html',
        templates=templates,
        template_type_options=template_type_options,
        incident_type_options=incident_type_options,
        current_filters={
            'type': template_type,
            'incident_type': incident_type
        }
    )

@app.route('/communications/templates/create', methods=['GET', 'POST'])
@login_required
@requires_role(['admin', 'manager'])
def create_communication_template():
    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')
        body = request.form.get('body')
        template_type = request.form.get('template_type')
        incident_type = request.form.get('incident_type')
        
        # Validate required fields
        if not all([name, subject, body, template_type]):
            flash('Please fill in all required fields', 'danger')
            return render_template(
                'communications/create.html',
                template_type_options=['internal', 'external', 'executive', 'customer'],
                incident_type_options=incident_type_options
            )
        
        # Create template
        template = CommunicationTemplate(
            name=name,
            subject=subject,
            body=body,
            template_type=template_type,
            incident_type=incident_type if incident_type else None,
            created_by=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        flash('Communication template created successfully', 'success')
        return redirect(url_for('list_communication_templates'))
    
    return render_template(
        'communications/create.html',
        template_type_options=['internal', 'external', 'executive', 'customer'],
        incident_type_options=incident_type_options
    )

# ------------------------------------------------------
# PIR Routes
# ------------------------------------------------------

@app.route('/pir')
@login_required
def list_pirs():
    pirs = PIR.query.order_by(PIR.conducted_at.desc()).all()
    return render_template('pir/list.html', pirs=pirs)

@app.route('/pir/create/<int:incident_id>', methods=['GET', 'POST'])
@login_required
def create_pir(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    
    # Check if PIR already exists for this incident
    existing_pir = PIR.query.filter_by(incident_id=incident_id).first()
    if existing_pir:
        flash('A PIR already exists for this incident', 'warning')
        return redirect(url_for('view_pir', pir_id=existing_pir.id))
    
    if request.method == 'POST':
        summary = request.form.get('summary')
        what_happened = request.form.get('what_happened')
        what_went_well = request.form.get('what_went_well')
        what_went_poorly = request.form.get('what_went_poorly')
        root_cause = request.form.get('root_cause')
        action_items_json = request.form.get('action_items')
        lessons_learned = request.form.get('lessons_learned')
        
        # Validate required fields
        if not all([summary, what_happened, what_went_well, what_went_poorly, root_cause, lessons_learned]):
            flash('Please fill in all required fields', 'danger')
            return render_template('pir/create.html', incident=incident)
        
        # Parse action items JSON
        try:
            action_items = json.loads(action_items_json)
        except json.JSONDecodeError:
            flash('Invalid action items format', 'danger')
            return render_template('pir/create.html', incident=incident)
        
        # Create PIR
        pir = PIR(
            incident_id=incident_id,
            conducted_by=current_user.id,
            summary=summary,
            what_happened=what_happened,
            what_went_well=what_went_well,
            what_went_poorly=what_went_poorly,
            root_cause=root_cause,
            action_items=action_items,
            lessons_learned=lessons_learned
        )
        
        db.session.add(pir)
        db.session.commit()
        
        flash('Post-Incident Review created successfully', 'success')
        return redirect(url_for('view_pir', pir_id=pir.id))
    
    return render_template('pir/create.html', incident=incident)

@app.route('/pir/<int:pir_id>')
@login_required
def view_pir(pir_id):
    pir = PIR.query.get_or_404(pir_id)
    return render_template('pir/view.html', pir=pir)

# ------------------------------------------------------
# Reporting Routes
# ------------------------------------------------------

@app.route('/reports/metrics')
@login_required
@requires_role(['admin', 'manager'])
def metrics_report():
    metrics = get_incident_metrics()
    
    # Get top incident types
    top_types = db.session.query(
        Incident.incident_type, db.func.count(Incident.id).label('count')
    ).group_by(Incident.incident_type).order_by(db.func.count(Incident.id).desc()).limit(5).all()
    
    # Get average resolution times by severity
    avg_times = db.session.query(
        Incident.severity,
        db.func.avg(db.func.julianday(Incident.resolution_time) - db.func.julianday(Incident.detection_time)) * 24
    ).filter(
        Incident.detection_time.isnot(None),
        Incident.resolution_time.isnot(None)
    ).group_by(Incident.severity).all()
    
    # Time-based metrics
    time_periods = ['7days', '30days', '90days', 'all']
    time_metrics = {}
    
    for period in time_periods:
        time_metrics[period] = get_incident_metrics(period)
    
    return render_template(
        'reports/metrics.html',
        metrics=metrics,
        top_types=top_types,
        avg_times=avg_times,
        time_metrics=time_metrics
    )

# ------------------------------------------------------
# Error Handlers
# ------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
