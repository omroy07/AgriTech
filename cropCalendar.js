// 1. RESTRUCTURED DATA: Grouped by Country
const cropData = {
    "India": [
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
    ],
    "USA": [
        { crop: "Wheat (Winter)", sowing: 9, harvesting: 7 },
        { crop: "Corn (Maize)", sowing: 4, harvesting: 10 },
        { crop: "Soybean", sowing: 5, harvesting: 10 },
        { crop: "Cotton", sowing: 5, harvesting: 11 },
        { crop: "Rice", sowing: 4, harvesting: 9 }
    ],
    "Australia": [
        { crop: "Wheat", sowing: 4, harvesting: 11 },
        { crop: "Barley", sowing: 5, harvesting: 11 },
        { crop: "Canola", sowing: 4, harvesting: 11 }
    ]
};

const months = ["Crop", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];


// Initialize
document.addEventListener("DOMContentLoaded", function() {
    populateCountryDropdown();
    updateCropDropdown(); // Populate crops based on default country
    
    const calendar = document.getElementById("calendar");
    showLoadingState(calendar);
    
    setTimeout(() => {
        renderCalendar();
    }, 500);

    enableTooltipToggleOnTouch();
});


// Helper: Populate Country Dropdown
function populateCountryDropdown() {
    const countrySelect = document.getElementById("countrySelect");
    const countries = Object.keys(cropData);
    
    countries.forEach(country => {
        const option = document.createElement("option");
        option.value = country;
        option.innerText = country;
        countrySelect.appendChild(option);
    });
}


// Helper: Update Crop Dropdown based on selected Country
function updateCropDropdown() {
    const country = document.getElementById("countrySelect").value;
    const cropSelect = document.getElementById("cropSelect");
    
    // Reset options
    cropSelect.innerHTML = '<option value="all">View All Crops</option>';
    
    // Get crops for selected country
    const availableCrops = cropData[country] || [];
    
    availableCrops.forEach(item => {
        const option = document.createElement("option");
        option.value = item.crop;
        option.innerText = item.crop;
        cropSelect.appendChild(option);
    });
}


function renderCalendar() {
    const calendar = document.getElementById("calendar");
    // Ensure we get values safely
    const countrySelect = document.getElementById("countrySelect");
    const cropSelect = document.getElementById("cropSelect");
    
    const countryFilter = countrySelect ? countrySelect.value : "India";
    const cropFilter = cropSelect ? cropSelect.value : "all";

    showLoadingState(calendar);
    
    setTimeout(() => {
        renderCalendarContent(countryFilter, cropFilter);
    }, 300);
}


function showLoadingState(calendar) {
    calendar.classList.add("loading");
    calendar.innerHTML = `
        <div class="calendar-loading">
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading crop calendar...</div>
        </div>
    `;
}


function renderCalendarContent(country, cropFilter) {
    const calendar = document.getElementById("calendar");
    calendar.innerHTML = "";
    calendar.classList.remove("loading");
    
    // Render Header Row
    months.forEach((month, index) => {
        const div = document.createElement("div");
        div.className = "month";
        div.innerText = month;
        div.style.animationDelay = `${index * 0.05}s`;
        calendar.appendChild(div);
    });

    // 1. Get crops for the selected country
    const countryCrops = cropData[country] || [];

    // 2. Filter specific crop if selected
    const filteredCrops = countryCrops.filter(item => cropFilter === "all" || item.crop === cropFilter);
    
    // If no data found
    if (filteredCrops.length === 0) {
        // Create a full-width message
        const messageDiv = document.createElement("div");
        messageDiv.style.gridColumn = "1 / -1";
        messageDiv.style.textAlign = "center";
        messageDiv.style.padding = "2rem";
        messageDiv.innerText = "No data available for this selection.";
        calendar.appendChild(messageDiv);
        return;
    }

    // Render Rows
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
        
        console.log(`${cropName} - ${phase} phase clicked`);
    });
}


// --- EVENT LISTENERS ---

// 1. Country Selection Change
document.getElementById("countrySelect").addEventListener("change", function () {
    const calendar = document.getElementById("calendar");
    
    // Visual feedback
    calendar.style.opacity = "0.5";
    calendar.style.transform = "translateY(10px)";
    
    // Update the Crop list because different countries grow different crops
    updateCropDropdown();

    setTimeout(() => {
        renderCalendar();
        
        // Fade back in
        setTimeout(() => {
            calendar.style.opacity = "1";
            calendar.style.transform = "translateY(0)";
        }, 100);
    }, 200);
});


// 2. Crop Selection Change
document.getElementById("cropSelect").addEventListener("change", function () {
    const calendar = document.getElementById("calendar");
    
    calendar.style.opacity = "0.5";
    calendar.style.transform = "translateY(10px)";
    
    setTimeout(() => {
        renderCalendar();
        
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


function enableTooltipToggleOnTouch() {
  const isTouchDevice = window.matchMedia("(hover: none) and (pointer: coarse)").matches;
  if (!isTouchDevice) return; // Only apply on touch devices

  const calendar = document.getElementById("calendar");

  // Track currently open tooltip
  let activeTooltipCell = null;

  calendar.addEventListener("click", (e) => {
    const cell = e.target.closest(".month-cell");
    if (!cell) return;

    const tooltip = cell.querySelector(".tooltip");
    if (!tooltip) return;

    // If clicking the same cell, toggle tooltip
    if (activeTooltipCell === cell) {
      tooltip.style.visibility = "hidden";
      tooltip.style.opacity = "0";
      activeTooltipCell = null;
    } else {
      // Hide previously active tooltip
      if (activeTooltipCell) {
        const prevTooltip = activeTooltipCell.querySelector(".tooltip");
        if (prevTooltip) {
          prevTooltip.style.visibility = "hidden";
          prevTooltip.style.opacity = "0";
        }
      }
      // Show current tooltip
      tooltip.style.visibility = "visible";
      tooltip.style.opacity = "1";
      activeTooltipCell = cell;
    }
  });

  // Hide tooltip if clicking outside calendar cells
  document.addEventListener("click", (e) => {
    if (!calendar.contains(e.target)) {
      if (activeTooltipCell) {
        const tooltip = activeTooltipCell.querySelector(".tooltip");
        if (tooltip) {
          tooltip.style.visibility = "hidden";
          tooltip.style.opacity = "0";
        }
        activeTooltipCell = null;
      }
    }
  });
}