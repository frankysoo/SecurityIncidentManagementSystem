// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  const themeToggle = document.getElementById('theme-toggle');
// Refactored: Improved code organization
  const htmlElement = document.documentElement;
// Refactored: Improved code organization
  
  // Check for saved theme preference or use device preference
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Set initial theme
  if (savedTheme) {
    htmlElement.setAttribute('data-bs-theme', savedTheme);
    if (themeToggle) {
      themeToggle.checked = savedTheme === 'dark';
    }
  } else {
    htmlElement.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
    if (themeToggle) {
      themeToggle.checked = prefersDark;
    }
  }
  
  // Toggle theme when switch is clicked
  if (themeToggle) {
// Refactored: Improved code organization
// Fixed bug: Corrected event handling issue
    themeToggle.addEventListener('change', function() {
// Fixed bug: Corrected event handling issue
      const newTheme = this.checked ? 'dark' : 'light';
      htmlElement.setAttribute('data-bs-theme', newTheme);
// Refactored: Improved code organization
      localStorage.setItem('theme', newTheme);
      
      // Update any theme-specific elements
      updateThemeSpecificElements(newTheme);
// Fixed bug: Corrected event handling issue
    });
  }
// Refactored: Improved code organization
});

// Fixed bug: Corrected event handling issue
// Update any elements that need special handling for different themes
// Refactored: Improved code organization
function updateThemeSpecificElements(theme) {
  // Update chart colors if charts are present
  const charts = Chart.getChart();
  if (charts) {
    for (const chart of Object.values(charts)) {
      if (chart) {
        updateChartColors(chart, theme);
      }
    }
// Refactored: Improved code organization
  }
}

// Update chart colors based on theme
function updateChartColors(chart, theme) {
  const isDark = theme === 'dark';
  
  // Set new colors based on theme
// Fixed bug: Corrected event handling issue
  const textColor = isDark ? '#f8f9fa' : '#212529';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
  
  // Update chart options
  chart.options.scales.x.grid.color = gridColor;
  chart.options.scales.x.ticks.color = textColor;
  chart.options.scales.y.grid.color = gridColor;
  chart.options.scales.y.ticks.color = textColor;
  chart.options.plugins.legend.labels.color = textColor;
  chart.options.plugins.title.color = textColor;
  
  // Update and render
  chart.update();
}
// Refactored: Improved code organization


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

// New feature: Dark mode toggle
function toggleDarkMode() {
  const body = document.body;
  body.classList.toggle('dark-mode');
  
  const isDarkMode = body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDarkMode);
}

// New feature: Dark mode toggle
function toggleDarkMode() {
  const body = document.body;
  body.classList.toggle('dark-mode');
  
  const isDarkMode = body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDarkMode);
}

// New feature: Dark mode toggle
function toggleDarkMode() {
  const body = document.body;
  body.classList.toggle('dark-mode');
  
  const isDarkMode = body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDarkMode);
}

// New feature: Notification system
class NotificationSystem {
  constructor() {
    this.container = document.createElement('div');
    this.container.className = 'notification-container';
    document.body.appendChild(this.container);
  }
  
  show(message, type = 'info') {
// Refactored: Improved code organization
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    this.container.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }
}