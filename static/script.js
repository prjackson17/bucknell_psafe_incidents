function loadReport() {
    const date = document.getElementById('reportDate').value;
    if (!date) {
      alert('Please select a date');
      return;
    }
  
    fetch(`/reports/crime_log_${date}.json`)
        .then(response => {
        if (!response.ok) {
            throw new Error('No report found for this date');
        }
        return response.json();
        })
        .then(data => {
        displayReport(data);
        })
        .catch(err => {
        document.getElementById('reportOutput').innerHTML = `<p style="color:red;">Error loading report: ${err.message}</p>`;
        });
}
  
function displayReport(data) {
    const container = document.getElementById('reportOutput');
    container.innerHTML = ''; // Clear any previous content
  
    if (!Array.isArray(data) || data.length === 0) {
        container.innerHTML = '<p>No incidents found for this date.</p>';
        return;
    }
  
    data.forEach((entry, index) => {
        const card = document.createElement('div');
        card.classList.add('incident-card');

        card.innerHTML = `
        <h3>Incident ${index + 1}</h3>
        <p>Case <strong>${entry["Case Number"] || 'N/A'}</strong></p>
        <p>${entry["Date"] || 'N/A'} - ${entry["Time"] || 'N/A'}</p>
        <p>at <strong>${entry["Location"] || 'N/A'}</strong></p>
        <p>${entry["Nature"] || 'N/A'}</p>
        `

        container.appendChild(card);
    });
}   

function loadMonthlyStats() {
    fetch('/api/stats/monthly')
        .then(response => response.json())
        .then(data => {
            const currentYear = new Date().getFullYear();
            const minYear = 2024; // Adjust as needed

            // Filter out unreasonable years
            const filteredEntries = Object.entries(data).filter(([key, value]) => {
                const year = parseInt(key.split('-')[0]);
                return year >= minYear && year <= currentYear;
            });

            // Sort by date
            filteredEntries.sort((a, b) => a[0].localeCompare(b[0]));

            // Prepare chart data
            const labels = filteredEntries.map(([key]) => key);
            const values = filteredEntries.map(([_, val]) => val);

            renderChart(labels, values);
        })
        .catch(err => {
            console.error("Failed to load monthly stats:", err);
            document.getElementById('chartError').textContent = "Failed to load stats.";
        });
}

let chart;

function renderChart(labels, values) {
    const chartEl = document.getElementById('monthlyChart');
    if (!chartEl) {
        console.error("Chart canvas not found!");
        return;
    }

    const ctx = chartEl.getContext('2d');

    if (chart) chart.destroy();

    // Compute Weighted Moving Average
    const weights = [3, 2, 1]; // 3 month WMA
    const wma = computeWeightedMovingAverage(values, weights);

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Reports per Month',
                    data: values,
                    backgroundColor: 'lightblue',
                    borderColor: 'blue',
                    borderWidth: 1,
                },
                {
                    label: 'Weighted Moving Average',
                    data: wma,
                    type: 'line',
                    borderColor: 'orange',
                    backgroundColor: 'transparent',
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2,
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Reports'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}


function computeWeightedMovingAverage(data, weights) {
    const wma = [];
    const weightSum = weights.reduce((a, b) => a + b, 0);
    const n = weights.length;

    for (let i = 0; i < data.length; i++) {
        if (i < n - 1) {
            wma.push(null); // not enough data for full window
        } else {
            let weightedSum = 0;
            for (let j = 0; j < n; j++) {
                weightedSum += data[i - j] * weights[j];
            }
            wma.push(weightedSum / weightSum);
        }
    }

    return wma;
}

function clearReport() {
    document.getElementById('reportOutput').textContent = '';
}

function formatDate(date) {
    // Format date as YYYY-MM-DD to match your filenames
    return date.toISOString().slice(0, 10);
}
  
async function loadRecentReports() {
    const container = document.getElementById('recentReports');
    container.innerHTML = ''; // clear previous

    const today = new Date();

    for (let i = 2; i <= 6; i++) {  // previous 5 days, excluding today
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const formattedDate = formatDate(date);

        try {
            const response = await fetch(`/reports/crime_log_${formattedDate}.json`);
            if (!response.ok) {
                throw new Error('No report found for this date');
            }
            const data = await response.json();

            // Create a single incident card for the date
            const card = document.createElement('div');
            card.classList.add('incident-card');

            card.innerHTML = `
                <h3>Report for ${formattedDate}</h3>
                ${data.map((entry, index) => `
                    <div>
                        <h4>Incident ${index + 1}</h4>
                        <p>Case <strong>${entry["Case Number"] || 'N/A'}</strong></p>
                        <p>${entry["Date"] || 'N/A'} - ${entry["Time"] || 'N/A'}</p>
                        <p>at <strong>${entry["Location"] || 'N/A'}</strong></p>
                        <p>${entry["Nature"] || 'N/A'}</p>
                    </div>
                `).join('')}
            `;

            container.appendChild(card);
        } catch (error) {
            // Optionally show message if missing
            const noReport = document.createElement('div');
            noReport.classList.add('no-report');
            noReport.textContent = `No report found for ${formattedDate}`;
            container.appendChild(noReport);
        }
    }
}

// sets the max date for the date input to 2 days ago
function getMaxDate() {
    const dateInput = document.getElementById('reportDate');
    const twoDaysAgo = new Date();
    twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
    const formattedDate = twoDaysAgo.toISOString().split('T')[0];

    dateInput.value = formattedDate;
    dateInput.max = formattedDate;
}

document.addEventListener("DOMContentLoaded", () => {
    loadMonthlyStats();
    loadRecentReports();
    getMaxDate();
});