document.addEventListener('DOMContentLoaded', () => {
    // Default location for demo (In real app, fetch from user profile)
    const userLocation = "Punjab, India";

    fetchWeather(userLocation);
    fetchAdvisories();
});

async function fetchWeather(location) {
    try {
        const response = await fetch(`/api/v1/weather/current?location=${encodeURIComponent(location)}`);
        const data = await response.json();

        if (data.status === 'success') {
            const w = data.data;
            document.getElementById('current-loc').textContent = w.location;
            document.getElementById('current-temp').textContent = `${Math.round(w.temperature)}°C`;
            document.getElementById('current-cond').textContent = w.weather_condition;
            document.getElementById('humidity-val').textContent = `${w.humidity}%`;
            document.getElementById('wind-val').textContent = `${w.wind_speed} km/h`;
        }
    } catch (error) {
        console.error('Weather fetch error:', error);
    }
}

async function fetchAdvisories() {
    const list = document.getElementById('advisory-list');

    try {
        const response = await fetch('/api/v1/advisories/');
        const data = await response.json();

        if (data.status === 'success') {
            renderAdvisories(data.data);
        }
    } catch (error) {
        console.error('Advisory fetch error:', error);
        list.innerHTML = '<p>Engine offline. Please try again later.</p>';
    }
}

function renderAdvisories(advisories) {
    const list = document.getElementById('advisory-list');
    list.innerHTML = '';

    if (advisories.length === 0) {
        list.innerHTML = '<div class="loading-state"><p>No advisories found. Subscribe to crops to receive AI insights.</p></div>';
        return;
    }

    advisories.forEach(adv => {
        const card = document.createElement('div');
        card.className = `advisory-card ${adv.priority.toLowerCase()}-priority`;

        card.innerHTML = `
            <span class="priority-badge">${adv.priority}</span>
            <div class="crop-label">${adv.crop_name} • ${adv.growth_stage || 'Growth'}</div>
            <div class="advisory-text">${formatText(adv.advisory_text)}</div>
            <div class="footer-info">
                <span>Generated ${formatDate(adv.created_at)}</span>
                <div style="cursor: pointer;" onclick="provideFeedback(${adv.id})">
                    <i class="far fa-star"></i> Feedback
                </div>
            </div>
        `;
        list.appendChild(card);
    });
}

function formatText(text) {
    // Simple markdown-ish conversion for the demo
    return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString();
}

async function provideFeedback(id) {
    const { value: rating } = await Swal.fire({
        title: 'Rate this advisory',
        input: 'range',
        inputLabel: 'Was this recommendation helpful?',
        inputAttributes: { min: 1, max: 5, step: 1 },
        inputValue: 5
    });

    if (rating) {
        try {
            await fetch(`/api/v1/advisories/${id}/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rating: parseInt(rating) })
            });
            Swal.fire('Thank you!', 'Your feedback helps improve our AI engine.', 'success');
        } catch (e) { }
    }
}
