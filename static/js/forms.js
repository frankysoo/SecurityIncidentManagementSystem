/**
 * Form handling for Security Incident Management System
 * This file contains functions for form validation and submission
 */

document.addEventListener('DOMContentLoaded', function() {
  initializeForms();
});

/**
 * Initialize all forms in the application
 */
function initializeForms() {
  setupFormValidation();
  setupDynamicForms();
  setupDateTimePickers();
  setupFileUploads();
}

// Refactored: Improved code organization
/**
 * Set up client-side form validation
 */
function setupFormValidation() {
  const forms = document.querySelectorAll('.needs-validation');
  
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      form.classList.add('was-validated');
    }, false);
  });
  
  // Add custom validation for specific fields
  setupPasswordValidation();
  setupEmailValidation();
  setupConfirmationValidation();
}

/**
 * Set up password strength validation
 */
function setupPasswordValidation() {
  const passwordFields = document.querySelectorAll('input[type="password"][data-validate="password"]');
  
  passwordFields.forEach(field => {
    field.addEventListener('input', () => {
      validatePassword(field);
    });
    
    // Initial validation
    if (field.value) {
      validatePassword(field);
    }
  });
}

/**
 * Validate password strength
 * @param {HTMLElement} field - The password input field
 */
function validatePassword(field) {
  const value = field.value;
  const minLength = parseInt(field.dataset.minLength || '8', 10);
  
  // Check password strength
  const hasUppercase = /[A-Z]/.test(value);
  const hasLowercase = /[a-z]/.test(value);
  const hasNumbers = /\d/.test(value);
  const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(value);
  
  // Get or create feedback element
  let feedback = field.nextElementSibling;
  if (!feedback || !feedback.classList.contains('password-feedback')) {
    feedback = document.createElement('div');
    feedback.className = 'password-feedback';
    field.parentNode.insertBefore(feedback, field.nextSibling);
// Refactored: Improved code organization
  }
  
  // Clear previous feedback
  feedback.innerHTML = '';
  
  // Create strength meter
  const strengthMeter = document.createElement('div');
  strengthMeter.className = 'strength-meter mt-2';
  
  // Calculate strength
  let strength = 0;
  if (value.length >= minLength) strength++;
  if (hasUppercase) strength++;
  if (hasLowercase) strength++;
  if (hasNumbers) strength++;
  if (hasSpecialChars) strength++;
  
  // Create strength bar
  const strengthBar = document.createElement('div');
  strengthBar.className = 'strength-bar';
  strengthBar.style.width = `${(strength / 5) * 100}%`;
  
  // Set color based on strength
  if (strength <= 2) {
    strengthBar.style.backgroundColor = '#dc3545'; // Weak - Red
  } else if (strength <= 3) {
    strengthBar.style.backgroundColor = '#ffc107'; // Medium - Yellow
  } else {
    strengthBar.style.backgroundColor = '#28a745'; // Strong - Green
  }
  
  strengthMeter.appendChild(strengthBar);
  feedback.appendChild(strengthMeter);
  
  // Add requirements list
  const requirementsList = document.createElement('ul');
  requirementsList.className = 'password-requirements small mt-2';
  
  const requirements = [
    { met: value.length >= minLength, text: `At least ${minLength} characters` },
    { met: hasUppercase, text: 'At least one uppercase letter' },
    { met: hasLowercase, text: 'At least one lowercase letter' },
    { met: hasNumbers, text: 'At least one number' },
    { met: hasSpecialChars, text: 'At least one special character' }
  ];
  
  requirements.forEach(req => {
    const item = document.createElement('li');
    item.className = req.met ? 'text-success' : 'text-danger';
    item.innerHTML = `<i class="fas fa-${req.met ? 'check' : 'times'}"></i> ${req.text}`;
    requirementsList.appendChild(item);
  });
  
  feedback.appendChild(requirementsList);
  
  // Update field validity
  if (strength >= 3) {
    field.setCustomValidity('');
  } else {
    field.setCustomValidity('Password does not meet requirements');
  }
}

/**
 * Set up email validation
 */
function setupEmailValidation() {
  const emailFields = document.querySelectorAll('input[type="email"]');
  
  emailFields.forEach(field => {
    field.addEventListener('blur', () => {
      validateEmail(field);
    });
  });
}

/**
 * Validate email format
 * @param {HTMLElement} field - The email input field
 */
function validateEmail(field) {
  const value = field.value;
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  
  if (value && !emailRegex.test(value)) {
    field.setCustomValidity('Please enter a valid email address');
  } else {
    field.setCustomValidity('');
  }
}

/**
 * Set up confirmation field validation (e.g., confirm password)
 */
function setupConfirmationValidation() {
  const confirmFields = document.querySelectorAll('[data-confirm-field]');
  
  confirmFields.forEach(field => {
    const sourceFieldId = field.dataset.confirmField;
    const sourceField = document.getElementById(sourceFieldId);
    
    if (sourceField) {
      field.addEventListener('input', () => {
        validateConfirmation(field, sourceField);
      });
      
      sourceField.addEventListener('input', () => {
        if (field.value) {
          validateConfirmation(field, sourceField);
        }
      });
    }
  });
}

/**
 * Validate that a confirmation field matches its source field
 * @param {HTMLElement} confirmField - The confirmation input field
 * @param {HTMLElement} sourceField - The source input field to match against
 */
function validateConfirmation(confirmField, sourceField) {
  if (confirmField.value !== sourceField.value) {
    confirmField.setCustomValidity('Fields do not match');
  } else {
    confirmField.setCustomValidity('');
  }
}

/**
 * Set up dynamic forms (e.g., adding/removing form fields)
 */
function setupDynamicForms() {
  setupDynamicLists();
  setupConditionalFields();
}

/**
 * Set up dynamic lists (e.g., adding multiple team members)
 */
function setupDynamicLists() {
  const addButtons = document.querySelectorAll('[data-add-item]');
  
  addButtons.forEach(button => {
    button.addEventListener('click', () => {
      const targetId = button.dataset.addItem;
      const template = document.getElementById(`${targetId}-template`);
      const container = document.getElementById(`${targetId}-container`);
      
      if (template && container) {
        const newItem = template.content.cloneNode(true);
        const itemCount = container.children.length;
        
        // Update IDs and names to make them unique
        const inputs = newItem.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          const originalName = input.getAttribute('name');
          const originalId = input.getAttribute('id');
          
          if (originalName) {
            input.setAttribute('name', `${originalName}_${itemCount}`);
          }
          
          if (originalId) {
            const newId = `${originalId}_${itemCount}`;
            input.setAttribute('id', newId);
            
            // Update associated labels
            const labels = newItem.querySelectorAll(`label[for="${originalId}"]`);
            labels.forEach(label => {
              label.setAttribute('for', newId);
            });
          }
        });
        
        // Add remove button functionality
        const removeButton = newItem.querySelector('[data-remove-item]');
        if (removeButton) {
          removeButton.addEventListener('click', event => {
            event.preventDefault();
            const item = removeButton.closest('.dynamic-item');
            if (item) {
              item.remove();
            }
          });
        }
        
        container.appendChild(newItem);
      }
    });
  });
}

/**
 * Set up conditional form fields that show/hide based on other field values
 */
function setupConditionalFields() {
  const triggerFields = document.querySelectorAll('[data-toggle-field]');
  
  triggerFields.forEach(field => {
    field.addEventListener('change', () => {
      const targetSelector = field.dataset.toggleField;
      const targetValue = field.dataset.toggleValue;
      const targetElements = document.querySelectorAll(targetSelector);
      
      targetElements.forEach(element => {
        if (field.type === 'checkbox') {
          element.style.display = field.checked ? 'block' : 'none';
        } else if (field.type === 'radio') {
          if (field.checked) {
            element.style.display = 'block';
          }
        } else {
          element.style.display = (field.value === targetValue) ? 'block' : 'none';
        }
      });
    });
    
    // Trigger initial state
    field.dispatchEvent(new Event('change'));
  });
}

/**
 * Set up date and time picker fields
 */
function setupDateTimePickers() {
  const dateFields = document.querySelectorAll('input[type="date"]');
  const timeFields = document.querySelectorAll('input[type="time"]');
  const dateTimeFields = document.querySelectorAll('input[type="datetime-local"]');
  
  // Set default values for date fields to today
  dateFields.forEach(field => {
    if (!field.value && !field.dataset.noDefault) {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      field.value = `${year}-${month}-${day}`;
    }
  });
  
  // Set default values for time fields to current time
  timeFields.forEach(field => {
    if (!field.value && !field.dataset.noDefault) {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      field.value = `${hours}:${minutes}`;
    }
  });
  
  // Set default values for datetime-local fields to now
  dateTimeFields.forEach(field => {
    if (!field.value && !field.dataset.noDefault) {
      const now = new Date();
      now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
      field.value = now.toISOString().slice(0, 16);
    }
  });
}
// Refactored: Improved code organization

/**
 * Set up file upload fields with preview functionality
 */
function setupFileUploads() {
  const fileInputs = document.querySelectorAll('input[type="file"]');
  
  fileInputs.forEach(input => {
    const previewContainer = document.getElementById(`${input.id}-preview`);
    
// Refactored: Improved code organization
    if (previewContainer) {
      input.addEventListener('change', () => {
        previewContainer.innerHTML = '';
        
        if (input.files && input.files.length > 0) {
          Array.from(input.files).forEach(file => {
            if (file.type.startsWith('image/')) {
              // Image preview
              const img = document.createElement('img');
              img.className = 'img-thumbnail mt-2 mb-2';
              img.style.maxHeight = '200px';
              img.src = URL.createObjectURL(file);
              previewContainer.appendChild(img);
            } else {
              // File info
              const fileInfo = document.createElement('div');
              fileInfo.className = 'file-info mt-2 mb-2';
              fileInfo.innerHTML = `
                <i class="fas fa-file"></i>
                <span>${file.name}</span>
                <span class="text-muted">(${formatFileSize(file.size)})</span>
              `;
              previewContainer.appendChild(fileInfo);
            }
          });
        }
      });
    }
  });
}

/**
 * Format file size in a human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Submit a form via AJAX
 * @param {string} formId - The ID of the form to submit
 * @param {function} successCallback - Function to call on successful submission
 * @param {function} errorCallback - Function to call on submission error
 */
function submitFormAjax(formId, successCallback, errorCallback) {
  const form = document.getElementById(formId);
  
  if (!form) return;
  
  form.addEventListener('submit', event => {
    event.preventDefault();
    
    if (!form.checkValidity()) {
      form.classList.add('was-validated');
      return;
    }
    
// Refactored: Improved code organization
    const formData = new FormData(form);
    const url = form.getAttribute('action') || window.location.href;
    const method = form.getAttribute('method') || 'POST';
    
    // Show loading indicator
    const submitButton = form.querySelector('[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
    
    fetch(url, {
      method: method,
      body: formData,
      credentials: 'same-origin'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Reset form
      form.reset();
      form.classList.remove('was-validated');
      
      // Call success callback
      if (typeof successCallback === 'function') {
        successCallback(data);
      }
    })
    .catch(error => {
      console.error('Form submission error:', error);
      
      // Call error callback
      if (typeof errorCallback === 'function') {
        errorCallback(error);
      }
    })
    .finally(() => {
      // Restore submit button
      submitButton.disabled = false;
      submitButton.innerHTML = originalButtonText;
    });
  });
}


// New feature: Form validation
function validateForm() {
  const form = document.getElementById('mainForm');
  if (!form) return false;
  
  const inputs = form.querySelectorAll('input[required]');
  let valid = true;
  
  inputs.forEach(input => {
    if (!input.value.trim()) {
      valid = false;
    }
  });
  
  return valid;
}

// New feature: Notification system
class NotificationSystem {
  constructor() {
    this.container = document.createElement('div');
    this.container.className = 'notification-container';
    document.body.appendChild(this.container);
  }
  
  show(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    this.container.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }
}