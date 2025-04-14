document.addEventListener('DOMContentLoaded', function() {
  // Load playbook steps when a playbook is selected
  const playbookSelect = document.getElementById('playbook_select');
  if (playbookSelect) {
    playbookSelect.addEventListener('change', function() {
      const playbookId = this.value;
      if (playbookId) {
        loadPlaybookSteps(playbookId);
      } else {
        document.getElementById('playbook_steps').innerHTML = '';
      }
    });
  }
  
  // Initialize sortable for playbook steps (reordering)
  const stepsContainer = document.getElementById('playbook_steps_sortable');
  if (stepsContainer && typeof Sortable !== 'undefined') {
    Sortable.create(stepsContainer, {
      animation: 150,
      handle: '.step-drag-handle',
      onEnd: function() {
        // Update step order after drag
        updateStepOrder();
      }
    });
  }
  
  // Step form validation
  const stepForm = document.getElementById('playbook_step_form');
  if (stepForm) {
    stepForm.addEventListener('submit', function(event) {
      const actionField = document.getElementById('step_actions');
      if (actionField && !actionField.value.trim()) {
        actionField.classList.add('is-invalid');
        event.preventDefault();
        alert('Please provide actions for this step');
      }
    });
  }
});

function loadPlaybookSteps(playbookId) {
  const stepsContainer = document.getElementById('playbook_steps');
  stepsContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p>Loading steps...</p></div>';
  
  fetch(`/api/playbooks/steps/${playbookId}`)
    .then(response => response.json())
    .then(steps => {
      if (steps.length === 0) {
        stepsContainer.innerHTML = '<div class="alert alert-info">No steps defined for this playbook yet.</div>';
        return;
      }
      
      let html = '<div class="list-group">';
      steps.forEach(step => {
        html += `
          <div class="list-group-item">
            <div class="d-flex w-100 justify-content-between">
              <h5 class="mb-1">${step.order}. ${step.title}</h5>
              <small>Est. Time: ${step.time_estimate || 'Not specified'}</small>
            </div>
            <p class="mb-1">${step.description || ''}</p>
            <div class="card mb-2">
              <div class="card-header">
                Actions to take
              </div>
              <div class="card-body">
                <p class="card-text">${step.actions}</p>
              </div>
            </div>
            <div class="d-flex justify-content-between">
              <small class="text-muted">Expected outcome: ${step.expected_outcome || 'Not specified'}</small>
              <small class="text-muted">Role: ${step.role_responsible || 'Any'}</small>
            </div>
          </div>
        `;
      });
      html += '</div>';
      
      stepsContainer.innerHTML = html;
    })
    .catch(error => {
      console.error('Error loading playbook steps:', error);
      stepsContainer.innerHTML = '<div class="alert alert-danger">Error loading playbook steps</div>';
    });
}

function updateStepOrder() {
  // This would be implemented to save the new order of steps after dragging
  const stepItems = document.querySelectorAll('#playbook_steps_sortable .step-item');
  const newOrder = Array.from(stepItems).map((item, index) => {
    return {
      id: item.dataset.stepId,
      order: index + 1
    };
  });
  
  // In a real implementation, you would send this data to the server
  console.log('New step order:', newOrder);
  
  // Example fetch request (not implemented in backend for this example)
  /*
  fetch('/api/playbooks/steps/reorder', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newOrder)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update UI to reflect the new order
      newOrder.forEach((item, index) => {
        const stepElement = document.querySelector(`.step-item[data-step-id="${item.id}"]`);
        const orderElement = stepElement.querySelector('.step-order');
        orderElement.textContent = (index + 1) + '.';
      });
    }
  });
  */
}
