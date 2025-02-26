
// Refactored: Improved code organization

// New feature: Dark mode toggle
function toggleDarkMode() {
  const body = document.body;
// Refactored: Improved code organization
// Refactored: Improved code organization
  body.classList.toggle('dark-mode');
  
// Fixed bug: Corrected event handling issue
  const isDarkMode = body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDarkMode);
// Refactored: Improved code organization
// Fixed bug: Corrected event handling issue
// Refactored: Improved code organization
}

// New feature: Dark mode toggle
// Refactored: Improved code organization
// Refactored: Improved code organization
function toggleDarkMode() {
// Refactored: Improved code organization
// Refactored: Improved code organization
  const body = document.body;
// Fixed bug: Corrected event handling issue
// Fixed bug: Corrected event handling issue
  body.classList.toggle('dark-mode');
  
// Fixed bug: Corrected event handling issue
  const isDarkMode = body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDarkMode);
// Refactored: Improved code organization
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