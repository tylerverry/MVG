async function fetchTramData() {
    try {
        const response = await fetch('/api/trams');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        displayTramData(data);
    } catch (error) {
        console.error('Error fetching tram data:', error);
        document.getElementById('tram-display').innerText = 'Failed to load tram data.';
    }
}

function displayTramData(data) {
    const { northbound, southbound, lastUpdated } = data;

    const tramDisplay = document.getElementById('tram-display');
    tramDisplay.innerHTML = `
        <h2>Northbound Trams</h2>
        <ul>
            ${northbound.map(tram => `<li>Line ${tram.line} to ${tram.destination} in ${tram.minutes} minutes</li>`).join('')}
        </ul>
        <h2>Southbound Trams</h2>
        <ul>
            ${southbound.map(tram => `<li>Line ${tram.line} to ${tram.destination} in ${tram.minutes} minutes</li>`).join('')}
        </ul>
        <p>Last updated: ${new Date(lastUpdated).toLocaleTimeString()}</p>
    `;
}

// Call fetchTramData when the page loads
fetchTramData();