document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze_btn');
    
    if (!analyzeBtn) {
        console.error("Error: analyze_btn not found in HTML");
        return;
    }

    analyzeBtn.addEventListener('click', async () => {
        console.log("Button clicked, gathering data...");

        const soilData = {
            n: parseInt(document.getElementById('n_level').value) || 0,
            p: parseInt(document.getElementById('p_level').value) || 0,
            k: parseInt(document.getElementById('k_level').value) || 0
        };
        const selectedCrop = document.getElementById('crop_select').value;

        analyzeBtn.innerText = "Processing...";
        
        try {
            const response = await fetch('/api/analyze-rotation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ soil_status: soilData, selected_crop: selectedCrop })
            });

            if (!response.ok) throw new Error(`Server error: ${response.status}`);

            const data = await response.json();
            console.log("Data received from server:", data);
            displayResults(data);
        } catch (error) {
            console.error("Fetch error:", error);
            alert("Could not connect to the analysis server. Check if app.py is running.");
        } finally {
            analyzeBtn.innerText = "Generate Analysis";
        }
    });
});

function displayResults(data) {
    const panel = document.getElementById('results-panel');
    const isDepleted = data.analysis.is_depleted;
    
    panel.innerHTML = `
        <div class="status-card ${isDepleted ? 'status-warn' : 'status-good'}">
            <h4>${isDepleted ? '⚠️ Soil Depletion Risk' : '✅ Sustainable Choice'}</h4>
            <p>Projected Nitrogen: ${data.analysis.nitrogen}</p>
            <p><strong>Recommendation:</strong> ${data.recommendation || 'Soil health is stable for the next cycle.'}</p>
        </div>
    `;
}