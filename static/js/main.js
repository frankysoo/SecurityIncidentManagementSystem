
// Refactored: Improved code organization

// New feature: Dark mode toggle
function toggleDarkMode() {
  const body = document.body;
  body.classList.toggle('dark-mode');
  
  const isDarkMode = body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDarkMode);
// Refactored: Improved code organization
}