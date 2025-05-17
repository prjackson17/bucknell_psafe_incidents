function loadReport() {
    const date = document.getElementById('reportDate').value;
    if (!date) {
        alert('Please select a date');
        return;
    }

    fetch(`/reports/${date}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('reportOutput').textContent = JSON.stringify(data, null, 2);
        })
        .catch(err => {
            document.getElementById('reportOutput').textContent = 'Error loading report.';
        });
}