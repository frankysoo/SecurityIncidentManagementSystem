document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if we're on the dashboard page
    if (document.getElementById('severityChart')) {
        initDashboardCharts();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Date range picker for reports
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', function() {
            // Ensure end date is not before start date
            if (endDateInput.value && new Date(endDateInput.value) < new Date(startDateInput.value)) {
                endDateInput.value = startDateInput.value;
            }
            endDateInput.min = startDateInput.value;
        });
        
        // Set initial min value for end date
        if (startDateInput.value) {
            endDateInput.min = startDateInput.value;
        }
    }
    
    // Filter form submission on incidents page
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Build query string from form values
            const formData = new FormData(filterForm);
            const params = new URLSearchParams();
            
            for (const [key, value] of formData.entries()) {
                if (value) {
                    params.append(key, value);
                }
            }
            
            // Navigate to incidents page with filters
            window.location.href = '/incidents?' + params.toString();
        });
        
        // Reset filters button
        const resetButton = document.getElementById('reset-filters');
        if (resetButton) {
            resetButton.addEventListener('click', function() {
                window.location.href = '/incidents';
            });
        }
    }
    
    // Toggle comment visibility based on private checkbox
    const privateCheckbox = document.getElementById('is_private');
    if (privateCheckbox) {
        privateCheckbox.addEventListener('change', function() {
            const label = document.querySelector('label[for="is_private"]');
            if (this.checked) {
                label.innerHTML = 'Private <i class="fas fa-lock"></i>';
            } else {
                label.innerHTML = 'Public <i class="fas fa-globe"></i>';
            }
        });
    }
});
