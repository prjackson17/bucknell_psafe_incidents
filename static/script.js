function loadReport() {
    const date = document.getElementById('reportDate').value;
    if (!date) {
        alert('Please select a date');
        return;
    }

    fetch(`/reports/crime_log_${date}.json`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('reportOutput').textContent = JSON.stringify(data, null, 2);
        })
        .catch(err => {
            document.getElementById('reportOutput').textContent = 'Error loading report.';
        });
}

async function loadMonthlyStats() {
    try {
        const response = await fetch('/api/stats/monthly');
        const data = await response.json();

        const labels = Object.keys(data); // e.g., ['2024-09', '2024-10', ...]
        const values = Object.values(data); // e.g., [12, 18, 9, ...]

        const ctx = document.getElementById('monthlyChart').getContext('2d');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Reports',
                    data: values,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Reports per Month'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month (YYYY-MM)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Crime Report Counts'
                    }
                }
            }
        });

    } catch (error) {
        console.error('Failed to load monthly stats:', error);
    }
}

// Call the function when the page loads
window.onload = loadMonthlyStats;