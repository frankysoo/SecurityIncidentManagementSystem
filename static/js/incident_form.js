document.addEventListener('DOMContentLoaded', function() {
  // Initialize date/time pickers for incident form
  const detectedAtInput = document.getElementById('detected_at');
  if (detectedAtInput) {
    // Set default value to current date/time
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    detectedAtInput.value = now.toISOString().slice(0, 16);
  }
  
  // Incident type selection
  const incidentTypeSelect = document.getElementById('incident_type');
  if (incidentTypeSelect) {
    incidentTypeSelect.addEventListener('change', function() {
      // Could be used to dynamically load relevant playbooks or fields
      // based on the selected incident type
    });
  }
  
  // Add validation for required fields
  const incidentForm = document.getElementById('incident_form');
  if (incidentForm) {
    incidentForm.addEventListener('submit', function(event) {
      let valid = true;
      
      // Check required fields
      const requiredFields = incidentForm.querySelectorAll('[required]');
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          field.classList.add('is-invalid');
          valid = false;
        } else {
          field.classList.remove('is-invalid');
        }
      });
      
      if (!valid) {
        event.preventDefault();
        alert('Please fill out all required fields');
      }
    });
  }
  
  // Incident update form
  const updateForm = document.getElementById('incident_update_form');
  if (updateForm) {
    const statusChangeSelect = document.getElementById('status_change');
    const updateTypeSelect = document.getElementById('update_type');
    
    // Show/hide status change dropdown based on update type
    if (updateTypeSelect && statusChangeSelect) {
      updateTypeSelect.addEventListener('change', function() {
        const statusChangeContainer = document.getElementById('status_change_container');
        if (this.value === 'Status Change') {
          statusChangeContainer.style.display = 'block';
          statusChangeSelect.setAttribute('required', 'required');
        } else {
          statusChangeContainer.style.display = 'none';
          statusChangeSelect.removeAttribute('required');
        }
      });
      
      // Trigger on load
      updateTypeSelect.dispatchEvent(new Event('change'));
    }
  }
});

// Function to confirm closing an incident
function confirmCloseIncident() {
  return confirm('Are you sure you want to close this incident? This should only be done when all activities are complete and documented.');
}

// Function to add dynamic form fields for team members
function addTeamMemberField() {
  const container = document.getElementById('team_members_container');
  const index = container.children.length;
  
  const div = document.createElement('div');
  div.className = 'row mb-3 team-member-row';
  div.innerHTML = `
    <div class="col-md-5">
      <select name="team_member_user_${index}" class="form-select" required>
        <option value="">Select User</option>
        <!-- User options would be populated by server -->
      </select>
    </div>
    <div class="col-md-5">
      <select name="team_member_role_${index}" class="form-select" required>
        <option value="">Select Role</option>
        <!-- Role options would be populated by server -->
      </select>
    </div>
    <div class="col-md-2">
      <button type="button" class="btn btn-danger" onclick="removeTeamMemberField(this)">
        <i class="fas fa-times"></i>
      </button>
    </div>
  `;
  
  container.appendChild(div);
  
  // In a real implementation, you would load users from an API
  // For this example, we'll just add placeholder options
  const userSelect = div.querySelector(`select[name="team_member_user_${index}"]`);
  ['User 1', 'User 2', 'User 3'].forEach((user, i) => {
    const option = document.createElement('option');
    option.value = i + 1;
    option.textContent = user;
    userSelect.appendChild(option);
  });
  
  // Same for roles
  const roleSelect = div.querySelector(`select[name="team_member_role_${index}"]`);
  ['Incident Commander', 'Technical Lead', 'Communications Manager'].forEach((role, i) => {
    const option = document.createElement('option');
    option.value = i + 1;
    option.textContent = role;
    roleSelect.appendChild(option);
  });
}

function removeTeamMemberField(button) {
  const row = button.closest('.team-member-row');
  row.remove();
}
