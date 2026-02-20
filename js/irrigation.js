// Location: /js/irrigation.js
const weatherSim = [
    { t: '22°C', s: 'Partly Cloudy', i: 'fa-cloud-sun', r: '30%', n: 'In 2 days' },
    { t: '30°C', s: 'Sunny', i: 'fa-sun', r: '5%', n: 'In 6 days' }
];

function initWeather() {
    const data = weatherSim[Math.floor(Math.random() * weatherSim.length)];
    document.getElementById('current-temp').innerText = data.t;
    document.getElementById('weather-status').innerText = data.s;
    document.getElementById('weather-icon').className = `fas ${data.i}`;
    document.getElementById('rain-chance').innerText = data.r;
    document.getElementById('next-rain').innerText = data.n;
}

document.getElementById('irrigation-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const moisture = document.getElementById('moisture').value;
    const crop = document.getElementById('crop-type').value;
    
    document.getElementById('result-section').classList.remove('hidden');
    const grid = document.getElementById('schedule-grid');
    grid.innerHTML = '';

    for (let i = 1; i <= 7; i++) {
        const needsWater = (moisture < 35) || (crop === "Rice" && i % 2 !== 0);
        grid.innerHTML += `
            <div class="day-block ${needsWater ? 'active' : ''}">
                <small>Day ${i}</small>
                <div style="margin: 8px 0;"><i class="fas ${needsWater ? 'fa-tint' : 'fa-check'}" 
                    style="color: ${needsWater ? '#3b82f6' : '#10b981'}"></i></div>
                <strong>${needsWater ? '12L' : '0L'}</strong>
            </div>
        `;
    }
});

document.getElementById('download-pdf').addEventListener('click', () => {
    const element = document.getElementById('result-section');
    html2pdf().from(element).save('Irrigation_Plan.pdf');
});

document.getElementById('moisture').addEventListener('input', (e) => {
    document.getElementById('moisture-val').innerText = e.target.value + '%';
});

window.onload = initWeather;