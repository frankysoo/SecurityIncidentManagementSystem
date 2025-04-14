// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  const themeToggle = document.getElementById('theme-toggle');
  const htmlElement = document.documentElement;
  
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
    themeToggle.addEventListener('change', function() {
      const newTheme = this.checked ? 'dark' : 'light';
      htmlElement.setAttribute('data-bs-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      
      // Update any theme-specific elements
      updateThemeSpecificElements(newTheme);
    });
  }
});

// Update any elements that need special handling for different themes
function updateThemeSpecificElements(theme) {
  // Update chart colors if charts are present
  const charts = Chart.getChart();
  if (charts) {
    for (const chart of Object.values(charts)) {
      if (chart) {
        updateChartColors(chart, theme);
      }
    }
  }
}

// Update chart colors based on theme
function updateChartColors(chart, theme) {
  const isDark = theme === 'dark';
  
  // Set new colors based on theme
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
