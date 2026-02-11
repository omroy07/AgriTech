function analyzeRisk() {
    const t = parseFloat(document.getElementById('temp').value);
    const h = parseFloat(document.getElementById('hum').value);
    const out = document.getElementById('risk-out');
    
    if (isNaN(t) || isNaN(h)) {
        out.innerText = "❌ Please enter valid data.";
        return;
    }

    if (t > 28 && h > 75) {
        out.innerHTML = "<span style='color:#c0392b'>⚠️ High Outbreak Risk</span>";
    } else if (t > 20 && h > 50) {
        out.innerHTML = "<span style='color:#f39c12'>⚠️ Moderate Risk</span>";
    } else {
        out.innerHTML = "<span style='color:#27ae60'>✅ Conditions Stable</span>";
    }
}

function findBeneficial() {
    const pest = document.getElementById('targetPest').value.toLowerCase();
    const out = document.getElementById('ben-out');
    const data = {
        "aphids": "Release Ladybugs (Coccinellidae)",
        "mites": "Deploy Predatory Mites",
        "caterpillar": "Use Bacillus thuringiensis (Bt)",
        "whitefly": "Deploy Encarsia formosa wasps"
    };

    out.innerText = data[pest] || "General Suggestion: Introduce Lacewings";
}

function startTracker() {
    let bar = document.getElementById('p-bar');
    let width = 0;
    bar.style.width = "0%";
    let id = setInterval(() => {
        if (width >= 100) clearInterval(id);
        else {
            width++;
            bar.style.width = width + "%";
        }
    }, 25);
}