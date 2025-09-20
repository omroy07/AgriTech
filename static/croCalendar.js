const crops = [
    { crop: "Wheat", sowing: 11, harvesting: 3 },
    { crop: "Rice", sowing: 6, harvesting: 10 },
    { crop: "Maize", sowing: 5, harvesting: 9 },
    { crop: "Barley", sowing: 11, harvesting: 4 },
    { crop: "Sugarcane", sowing: 2, harvesting: 12 },
    { crop: "Cotton", sowing: 6, harvesting: 11 },
    { crop: "Groundnut", sowing: 6, harvesting: 10 },
    { crop: "Soybean", sowing: 6, harvesting: 9 },
    { crop: "Pulses", sowing: 10, harvesting: 3 },
    { crop: "Mustard", sowing: 10, harvesting: 2 },
    { crop: "Sunflower", sowing: 1, harvesting: 4 },
    { crop: "Jute", sowing: 3, harvesting: 7 }
];


const months = ["Crop", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];


function renderCalendar(filter = "all") {
    const calendar = document.getElementById("calendar");
    
    // Show loading state
    showLoadingState(calendar);
    
    // Simulate loading delay for smooth transition
    setTimeout(() => {
        renderCalendarContent(filter);
    }, 300);
}

function showLoadingState(calendar) {
    calendar.innerHTML = `
        <div class="calendar-loading" style="grid-column: 1 / -1;">
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading crop calendar...</div>
        </div>
    `;
}

function renderCalendarContent(filter = "all") {
    const calendar = document.getElementById("calendar");
    calendar.innerHTML = "";
    
    // Header Row with staggered animation
    months.forEach((month, index) => {
        const div = document.createElement("div");
        div.className = "month";
        div.innerText = month;
        div.style.animationDelay = `${index * 0.05}s`;
        calendar.appendChild(div);
    });

    // Filter crops
    const filteredCrops = crops.filter(crop => filter === "all" || crop.crop === filter);
    
    // Render crops with staggered animation
    filteredCrops.forEach((crop, cropIndex) => {
        const row = [crop.crop, ...Array(12).fill("")];
        const start = crop.sowing;
        const end = crop.harvesting < start ? crop.harvesting + 12 : crop.harvesting;
        
        for (let i = start; i <= end; i++) {
            const monthIndex = i > 12 ? i - 12 : i;

            if (i === start) {
                row[monthIndex] = "sow";
            } else if (i === end) {
                row[monthIndex] = "harvest";
            } else {
                row[monthIndex] = "grow";
            }
        }

        row.forEach((cell, idx) => {
            const div = document.createElement("div");
            const animationDelay = (cropIndex * 0.1) + (idx * 0.02);
            div.style.animationDelay = `${animationDelay}s`;

            if (idx === 0) {
                div.className = "crop-name";
                div.innerText = crop.crop;
                div.setAttribute('role', 'rowheader');
                div.setAttribute('aria-label', `${crop.crop} crop row`);
            } else {
                div.className = `month-cell ${cell}`;
                div.setAttribute('role', 'gridcell');
                
                if (cell === "sow") {
                    div.innerHTML = `
                        <span class="emoji" role="img" aria-label="planting">🌱</span>
                        <div class="tooltip">Sowing season for ${crop.crop}</div>
                    `;
                    div.setAttribute('aria-label', `${crop.crop} sowing month`);
                    addCellInteractions(div, crop.crop, 'sowing');
                } else if (cell === "harvest") {
                    div.innerHTML = `
                        <span class="emoji" role="img" aria-label="harvesting">🌾</span>
                        <div class="tooltip">Harvesting season for ${crop.crop}</div>
                    `;
                    div.setAttribute('aria-label', `${crop.crop} harvesting month`);
                    addCellInteractions(div, crop.crop, 'harvesting');
                } else if (cell === "grow") {
                    div.innerHTML = `
                        <span class="emoji" role="img" aria-label="growing">🟩</span>
                        <div class="tooltip">Growing season for ${crop.crop}</div>
                    `;
                    div.setAttribute('aria-label', `${crop.crop} growing period`);
                    addCellInteractions(div, crop.crop, 'growing');
                }
            }

            calendar.appendChild(div);
        });
    });
}

function addCellInteractions(div, cropName, phase) {
    div.addEventListener("mouseenter", (e) => {
        e.target.style.transform = "translateY(-2px) scale(1.05)";
        e.target.style.zIndex = "10";
        
        // Show tooltip
        const tooltip = e.target.querySelector('.tooltip');
        if (tooltip) {
            tooltip.style.visibility = 'visible';
            tooltip.style.opacity = '1';
        }
    });

    div.addEventListener("mouseleave", (e) => {
        e.target.style.transform = "";
        e.target.style.zIndex = "";
        
        // Hide tooltip
        const tooltip = e.target.querySelector('.tooltip');
        if (tooltip) {
            tooltip.style.visibility = 'hidden';
            tooltip.style.opacity = '0';
        }
    });

    div.addEventListener("click", (e) => {
        // Add click feedback
        div.style.transform = "scale(0.95)";
        setTimeout(() => {
            div.style.transform = "";
        }, 150);
        
        // Show detailed info (placeholder for future enhancement)
        console.log(`${cropName} - ${phase} phase clicked`);
    });
}

// Enhanced dropdown event handler with smooth transitions
document.getElementById("cropSelect").addEventListener("change", function () {
    const selectedCrop = this.value;
    const calendar = document.getElementById("calendar");
    
    // Add fade out effect
    calendar.style.opacity = "0.5";
    calendar.style.transform = "translateY(10px)";
    
    setTimeout(() => {
        renderCalendar(selectedCrop);
        
        // Fade back in
        setTimeout(() => {
            calendar.style.opacity = "1";
            calendar.style.transform = "translateY(0)";
        }, 100);
    }, 200);
});

// Add keyboard navigation for accessibility
document.getElementById("cropSelect").addEventListener("keydown", function(e) {
    if (e.key === "Enter" || e.key === " ") {
        this.click();
    }
});

// Initialize calendar with enhanced loading
document.addEventListener("DOMContentLoaded", function() {
    // Add initial loading state
    const calendar = document.getElementById("calendar");
    showLoadingState(calendar);
    
    // Load calendar after a brief delay
    setTimeout(() => {
        renderCalendar();
    }, 500);
});
