document.addEventListener('DOMContentLoaded', function() {
    // Incident type change handler - load matching playbooks
    const incidentTypeSelect = document.getElementById('incident_type');
    const playbookContainer = document.getElementById('playbook-suggestions');
    
    if (incidentTypeSelect && playbookContainer) {
        incidentTypeSelect.addEventListener('change', function() {
            const incidentType = this.value;
            if (!incidentType) {
                playbookContainer.innerHTML = '';
                return;
            }
            
            fetch(`/api/playbooks/by-type?type=${encodeURIComponent(incidentType)}`)
                .then(response => response.json())
                .then(playbooks => {
                    if (playbooks.length === 0) {
                        playbookContainer.innerHTML = '<p>No playbooks found for this incident type.</p>';
                        return;
                    }
                    
                    let html = '<div class="mb-3"><h5>Suggested Playbooks</h5><ul class="list-group">';
                    playbooks.forEach(playbook => {
                        html += `
                            <li class="list-group-item">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>${playbook.title}</strong>
                                        ${playbook.description ? '<p class="mb-0 text-muted">' + playbook.description + '</p>' : ''}
                                    </div>
                                    <a href="/playbooks/${playbook.id}" target="_blank" class="btn btn-sm btn-outline-primary">View</a>
                                </div>
                            </li>
                        `;
                    });
                    html += '</ul></div>';
                    
                    playbookContainer.innerHTML = html;
                });
        });
        
        // Trigger on load if value already exists
        if (incidentTypeSelect.value) {
            incidentTypeSelect.dispatchEvent(new Event('change'));
        }
    }
    
    // Load communication templates based on incident type and severity
    const severitySelect = document.getElementById('severity');
    const communicationContainer = document.getElementById('communication-templates');
    
    function loadCommunicationTemplates() {
        if (!incidentTypeSelect || !severitySelect || !communicationContainer) return;
        
        const incidentType = incidentTypeSelect.value;
        const severity = severitySelect.value;
        
        if (!incidentType && !severity) {
            communicationContainer.innerHTML = '';
            return;
        }
        
        const params = new URLSearchParams();
        if (incidentType) params.append('type', incidentType);
        if (severity) params.append('severity', severity);
        
        fetch(`/api/templates/by-type?${params.toString()}`)
            .then(response => response.json())
            .then(templates => {
                if (templates.length === 0) {
                    communicationContainer.innerHTML = '<p>No communication templates found for this incident type and severity.</p>';
                    return;
                }
                
                let html = '<div class="mb-3"><h5>Communication Templates</h5><ul class="list-group">';
                templates.forEach(template => {
                    html += `
                        <li class="list-group-item">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${template.name}</strong>
                                    <p class="mb-0 text-muted">Audience: ${template.audience || 'Not specified'}</p>
                                </div>
                                <button type="button" class="btn btn-sm btn-outline-primary view-template" 
                                        data-bs-toggle="modal" data-bs-target="#templateModal"
                                        data-template-subject="${template.subject || ''}"
                                        data-template-body="${template.body}">
                                    View
                                </button>
                            </div>
                        </li>
                    `;
                });
                html += '</ul></div>';
                
                communicationContainer.innerHTML = html;
                
                // Add event listeners to view template buttons
                document.querySelectorAll('.view-template').forEach(button => {
                    button.addEventListener('click', function() {
                        const subject = this.getAttribute('data-template-subject');
                        const body = this.getAttribute('data-template-body');
                        
                        document.getElementById('templateModalLabel').textContent = subject || 'Communication Template';
                        document.getElementById('templateBody').textContent = body;
                    });
                });
            });
    }
    
    if (incidentTypeSelect && severitySelect && communicationContainer) {
        incidentTypeSelect.addEventListener('change', loadCommunicationTemplates);
        severitySelect.addEventListener('change', loadCommunicationTemplates);
        
        // Trigger on load if values already exist
        if (incidentTypeSelect.value || severitySelect.value) {
            loadCommunicationTemplates();
        }
    }
    
    // Dynamic fields for playbook steps
    const addStepButton = document.getElementById('add-step');
    const stepsContainer = document.getElementById('playbook-steps');
    let stepCount = document.querySelectorAll('.playbook-step').length;
    
    if (addStepButton && stepsContainer) {
        addStepButton.addEventListener('click', function() {
            stepCount++;
            
            const stepDiv = document.createElement('div');
            stepDiv.className = 'playbook-step card mb-3';
            stepDiv.innerHTML = `
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Step ${stepCount}</h5>
                    <button type="button" class="btn btn-sm btn-danger remove-step">Remove</button>
                </div>
                <div class="card-body">
                    <input type="hidden" name="step_id" value="">
                    <div class="mb-3">
                        <label for="step_title_${stepCount}" class="form-label">Title</label>
                        <input type="text" class="form-control" id="step_title_${stepCount}" name="step_title" required>
                    </div>
                    <div class="mb-3">
                        <label for="step_description_${stepCount}" class="form-label">Description</label>
                        <textarea class="form-control" id="step_description_${stepCount}" name="step_description" rows="3"></textarea>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="step_team_${stepCount}" class="form-label">Responsible Team</label>
                                <select class="form-select" id="step_team_${stepCount}" name="step_team">
                                    <option value="">Select Team</option>
                                    ${Array.from(document.querySelector('select[name="step_team"]')?.options || [])
                                        .map(opt => `<option value="${opt.value}">${opt.text}</option>`)
                                        .join('')}
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="step_time_${stepCount}" class="form-label">Estimated Time</label>
                                <input type="text" class="form-control" id="step_time_${stepCount}" name="step_time" placeholder="e.g., 15-30 minutes">
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            stepsContainer.appendChild(stepDiv);
            
            // Add event listener for remove button
            stepDiv.querySelector('.remove-step').addEventListener('click', function() {
                stepDiv.remove();
                // Recalculate step numbers
                document.querySelectorAll('.playbook-step').forEach((step, index) => {
                    step.querySelector('h5').textContent = `Step ${index + 1}`;
                });
                stepCount = document.querySelectorAll('.playbook-step').length;
            });
        });
        
        // Add event listeners for existing remove buttons
        document.querySelectorAll('.remove-step').forEach(button => {
            button.addEventListener('click', function() {
                this.closest('.playbook-step').remove();
                // Recalculate step numbers
                document.querySelectorAll('.playbook-step').forEach((step, index) => {
                    step.querySelector('h5').textContent = `Step ${index + 1}`;
                });
                stepCount = document.querySelectorAll('.playbook-step').length;
            });
        });
    }
});
