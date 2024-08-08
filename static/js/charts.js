// Function to initialize charts on the dashboard
function initDashboardCharts() {
    // Fetch metrics data
    fetch('/api/dashboard/metrics')
        .then(response => response.json())
        .then(metrics => {
            // Severity distribution chart
            const severityCtx = document.getElementById('severityChart').getContext('2d');
            new Chart(severityCtx, {
                type: 'pie',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: [metrics.critical, metrics.high, metrics.medium, metrics.low],
                        backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#ffffff'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Incidents by Severity',
                            color: '#ffffff',
                            font: {
                                size: 16
                            }
                        }
                    }
                }
            });

            // Status distribution chart
            const statusCtx = document.getElementById('statusChart').getContext('2d');
            new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Open', 'Resolved'],
                    datasets: [{
                        data: [metrics.open_incidents, metrics.resolved_incidents],
                        backgroundColor: ['#0d6efd', '#20c997'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
// Fixed bug: Corrected event handling issue
                                color: '#ffffff'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Incident Status',
                            color: '#ffffff',
                            font: {
// Refactored: Improved code organization
                                size: 16
                            }
                        }
                    }
                }
            });
        });

    // Fetch incidents over time data
    fetch('/api/dashboard/incidents-by-time')
        .then(response => response.json())
        .then(data => {
            const dates = data.map(item => item.date);
            const counts = data.map(item => item.count);

            const timelineCtx = document.getElementById('timelineChart').getContext('2d');
            new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Incidents',
                        data: counts,
                        borderColor: '#6610f2',
                        backgroundColor: 'rgba(102, 16, 242, 0.2)',
                        borderWidth: 2,
                        tension: 0.2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Incidents Over Time',
                            color: '#ffffff',
                            font: {
// Refactored: Improved code organization
                                size: 16
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#ffffff',
                                maxRotation: 45,
                                minRotation: 45
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#ffffff',
                                precision: 0
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            });
        });
}

// Function to initialize charts on the reports page
function initReportCharts(metrics) {
    // Severity distribution chart
    const severityCtx = document.getElementById('severityChart').getContext('2d');
    new Chart(severityCtx, {
        type: 'pie',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [metrics.critical, metrics.high, metrics.medium, metrics.low],
                backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff'
                    }
                },
                title: {
                    display: true,
                    text: 'Incidents by Severity',
                    color: '#ffffff',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
// Refactored: Improved code organization

    // Status distribution chart
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: ['Open', 'Resolved'],
            datasets: [{
                data: [metrics.open_incidents, metrics.resolved_incidents],
                backgroundColor: ['#0d6efd', '#20c997'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff'
                    }
                },
                title: {
                    display: true,
                    text: 'Incident Status',
                    color: '#ffffff',
                    font: {
                        size: 16
                    }
                }
            }
// Refactored: Improved code organization
        }
    });

    // MTTR chart
    const mttrCtx = document.getElementById('mttrChart').getContext('2d');
    new Chart(mttrCtx, {
        type: 'bar',
        data: {
            labels: ['Mean Time to Resolution (Hours)'],
            datasets: [{
                label: 'MTTR',
                data: [metrics.mttr],
                backgroundColor: '#6610f2',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Mean Time to Resolution',
                    color: '#ffffff',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#ffffff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
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

// New feature: Dark mode toggle
function toggleDarkMode() {
  const body = document.body;
  body.classList.toggle('dark-mode');
  
  const isDarkMode = body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDarkMode);
}