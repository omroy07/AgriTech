const pestDatabase = {
    "aphids": "Neem Oil Spray: Mix 2 tsp Neem oil with 1 tsp mild soap in 1L water. Spray leaves directly.",
    "slugs": "Eggshell Barrier: Crush eggshells and sprinkle around plant bases to deter soft-bodied pests.",
    "fungus": "Baking Soda Mix: 1 tbsp baking soda + 1 tsp liquid soap in 4L water. Prevents powdery mildew.",
    "ants": "Vinegar Barrier: Mix 50/50 vinegar and water. Spray around the perimeter of crop beds."
};

function startCompost() {
    let bar = document.getElementById("compost-bar");
    let status = document.getElementById("compost-status");
    let width = 0;
    let interval = setInterval(() => {
        if (width >= 100) { 
            clearInterval(interval); 
            status.innerHTML = "<strong>Status: Maturation (Ready for Field Use)</strong>";
        } else {
            width++;
            bar.style.width = width + "%";
            bar.innerText = width + "%";
            if(width < 30) status.innerText = "Status: Mesophilic Phase (Initial breakdown)";
            else if(width < 70) status.innerText = "Status: Thermophilic Phase (High heat)";
            else status.innerText = "Status: Cooling Phase (Final stabilization)";
        }
    }, 40);
}

function findRecipe() {
    let input = document.getElementById("pestInput").value.toLowerCase();
    let display = document.getElementById("recipe-display");
    if (input.length === 0) {
        display.innerText = "Start typing a pest name...";
        return;
    }
    display.innerText = pestDatabase[input] || "No organic recipe found. Try 'Aphids' or 'Slugs'.";
}

function calcSavings() {
    let liters = document.getElementById("liters").value;
    if (liters > 0) {
        let saved = liters * 0.25; // Logic: 25% efficiency increase with drip
        document.getElementById("save-result").innerText = `By switching to Drip Irrigation, you save approx ${saved.toFixed(2)} Liters daily!`;
    }
}