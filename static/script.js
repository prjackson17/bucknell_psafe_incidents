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
            document.getElementById('reportOutput').innerHTML = `<p>Error loading report: ${err.message}</p>`;
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

function convertToLocalTimeString(dateString, timeString) {
    if (!timeString || !dateString) return 'N/A';

    const fullDateTime = new Date(`${dateString}T${timeString}`);
    if (isNaN(fullDateTime)) return timeString; // fallback

    return fullDateTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function displayReport(data, date) {
    const container = document.getElementById('reportOutput');
    container.innerHTML = '';
    const niceDate = new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    if (!Array.isArray(data) || data.length === 0) {
        container.innerHTML = `<p>No incidents found for ${niceDate}.</p>`;
        return;
    }

    data.sort((a, b) => {
        const pad = t => t && t.match(/^\d{1,2}:\d{2}/) ? t.padStart(5, '0') : t;
        return pad(a["Time"] || '').localeCompare(pad(b["Time"] || ''));
    });

    data.forEach(entry => {
        const localTime = convertToLocalTimeString(date, entry["Time"]);
        const card = document.createElement('div');
        card.classList.add('incident-card');

        card.innerHTML = `
        <h3>${localTime}</h3>
        <p class="case-number">Case ${entry["Case Number"] || 'N/A'}</p>
        <p class="incident-details"><strong>${entry["Nature"] || 'N/A'}</strong> at <strong>${entry["Location"] || 'N/A'}</strong></p>
        `;

        container.appendChild(card);
    });
}

function loadMonthlyStats() {
    fetch('/api/stats/monthly')
        .then(response => response.json())
        .then(data => {
            const currentYear = new Date().getFullYear();
            const minYear = 2024;

            const filteredEntries = Object.entries(data).filter(([key]) => {
                const year = parseInt(key.split('-')[0]);
                return year >= minYear && year <= currentYear;
            });

            filteredEntries.sort((a, b) => a[0].localeCompare(b[0]));

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
let cardBGColor = '#063552';
let tanText = '#e8dac9';

function renderChart(labels, values) {
    const chartEl = document.getElementById('monthlyChart');
    if (!chartEl) {
        console.error("Chart canvas not found!");
        return;
    }

    const ctx = chartEl.getContext('2d');
    if (chart) chart.destroy();

    const weights = [3, 2, 1];
    const wma = computeWeightedMovingAverage(values, weights);

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '3-Month Weighted Moving Average',
                    data: wma,
                    type: 'line',
                    borderColor: '#f6ad55',
                    backgroundColor: 'transparent',
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2,
                },
                {
                    label: 'Reports per Month',
                    data: values,
                    backgroundColor: cardBGColor,
                    borderColor: cardBGColor,
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
                        color: tanText,
                        font: { weight: 'bold' }
                    },
                    ticks: {
                        color: tanText
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
                        color: tanText,
                        font: { weight: 'bold' }
                    },
                    ticks: {
                        color: tanText
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
                        color: tanText
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
            wma.push(null);
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
    return date.toISOString().slice(0, 10);
}

async function loadRecentReports() {
    const container = document.getElementById('recentReports');
    container.innerHTML = '';

    const today = new Date();

    for (let i = 2; i <= 6; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const formattedDate = formatDate(date);
        const niceDate = date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

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
            data.sort((a, b) => {
                const pad = t => t && t.match(/^\d{1,2}:\d{2}/) ? t.padStart(5, '0') : t;
                return pad(a["Time"] || '').localeCompare(pad(b["Time"] || ''));
            });

            card.innerHTML += data.map(entry => `
                <p><strong>${convertToLocalTimeString(formattedDate, entry["Time"])}</strong></p>
                <p>${entry["Nature"] || 'N/A'} at ${entry["Location"] || 'N/A'}</p>
            `).join('');
        }

        container.appendChild(card);
    }
}

// function getMaxDate() {
//     const dateInput = document.getElementById('reportDate');
//     const twoDaysAgo = new Date();
//     twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
//     const formattedDate = twoDaysAgo.toISOString().split('T')[0];

//     dateInput.value = formattedDate;
//     dateInput.max = formattedDate;
// }

function getMaxDate() {
    const dateInput = document.getElementById('reportDate');
    const now = new Date();
    // Set to midnight local time to avoid timezone issues
    now.setHours(0, 0, 0, 0);
    now.setDate(now.getDate() - 2);
    const formattedDate = now.toISOString().split('T')[0];

    dateInput.value = formattedDate;
    dateInput.max = formattedDate;
}

document.addEventListener("DOMContentLoaded", () => {
    loadMonthlyStats();
    loadRecentReports();
    getMaxDate();
});
