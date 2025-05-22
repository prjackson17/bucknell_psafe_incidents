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
            displayReport(data, date);
        })
        .catch(err => {
            document.getElementById('reportOutput').innerHTML = `<p style="color:red;">Error loading report: ${err.message}</p>`;
        });
}

function loadVedderBeach() {
    const date = '2024-02-02';

    fetch(`/reports/crime_log_${date}.json`)
        .then(response => {
            if (!response.ok) {
                throw new Error('No report found for this date');
            }
            return response.json();
        })
        .then(data => {
            displayReport(data, date);
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

    // Sort incidents by time (ascending)
    data.sort((a, b) => {
        const timeA = a["Time"] || '';
        const timeB = b["Time"] || '';
        // Pad times to ensure correct sorting (e.g., 9:05 -> 09:05)
        const pad = t => t && t.match(/^\d{1,2}:\d{2}/) ? t.padStart(5, '0') : t;
        return pad(timeA).localeCompare(pad(timeB));
    });

    data.forEach((entry, index) => {
        const card = document.createElement('div');
        card.classList.add('incident-card');

        card.innerHTML = `
        <h3>${entry["Time"] || 'N/A'}</h3>
        <p class="case-number">Case ${entry["Case Number"] || 'N/A'}</p>
        <p class="incident-details"><strong>${entry["Nature"] || 'N/A'}</strong> at <strong>${entry["Location"] || 'N/A'}</strong></p>
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

            // Prepare chart data with labels like "May 25"
            const labels = filteredEntries.map(([key]) => {
                const [year, month] = key.split('-');
                const date = new Date(year, parseInt(month) - 1);
                return date.toLocaleString('en-US', { month: 'short', year: '2-digit' }).replace(',', '');
            });
            const values = filteredEntries.map(([_, val]) => val);

            renderChart(labels, values);
        })
        .catch(err => {
            console.error("Failed to load monthly stats:", err);
            document.getElementById('chartError').textContent = "Failed to load stats.";
        });
}

let chart;
let cardBGColor = '#063552'; // blue gray
let tanText = '#e8dac9'; // tan

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
                    label: 'Weighted Moving Average',
                    data: wma,
                    type: 'line',
                    borderColor: '#f6ad55',     // lighter orange
                    backgroundColor: 'transparent',
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2,
                },
                {
                    label: 'Reports per Month',
                    data: values,
                    backgroundColor: '#2a4365', // dark blue
                    borderColor: '#1a365d',     // darker blue
                    borderWidth: 1,
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
                        text: 'Month',
                        color: cardBGColor,
                        font: { weight: 'bold' }
                    },
                    ticks: {
                        color: cardBGColor
                    },
                    grid: {
                        color: tanText
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Reports',
                        color: cardBGColor,
                        font: { weight: 'bold' }
                    },
                    ticks: {
                        color: cardBGColor
                    },
                    grid: {
                        color: tanText
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#2d3748'
                    }
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
        const niceDate = date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

        // Create a single incident card for the date
        const card = document.createElement('div');
        card.classList.add('incident-card');

        const response = await fetch(`/reports/crime_log_${formattedDate}.json`);
        if (!response.ok) {
            card.innerHTML = `<p>No report found for ${formattedDate}</p>`;
            container.appendChild(card);
            continue;
        }
        const data = await response.json();

        card.innerHTML = `<h3>${niceDate}</h3>`;

        if (!Array.isArray(data) || data.length === 0) {
            card.innerHTML += `<p>No incidents reported.</p>`;
        } else {
            // Sort incidents by time (ascending)
            data.sort((a, b) => {
                const timeA = a["Time"] || '';
                const timeB = b["Time"] || '';
                const pad = t => t && t.match(/^\d{1,2}:\d{2}/) ? t.padStart(5, '0') : t;
                return pad(timeA).localeCompare(pad(timeB));
            });

            card.innerHTML += data.map((entry) => `
                <p><strong>${entry["Time"] || 'N/A'}</strong></p>
                <p>${entry["Nature"] || 'N/A'} at ${entry["Location"] || 'N/A'}</p>
            `).join('');
        }

        container.appendChild(card);
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