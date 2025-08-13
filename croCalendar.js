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
    calendar.innerHTML = "";
 
    
    // Header Row
    months.forEach(month => {
        const div = document.createElement("div");
        div.className = "month";
        div.innerText = month;
        calendar.appendChild(div);
        

    });

    crops.forEach(crop => {
        if (filter !== "all" && crop.crop !== filter) return;

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

            if (idx === 0) {
                div.className = "crop-name";
                div.innerText = crop.crop;
            } else {
                div.className = `month-cell ${cell}`;
                if (cell === "sow") {
                    div.innerText = "🌱";
                    div.style.transition = "box-shadow 0.3s ease";
                    div.style.boxShadow = "0px 4px 6px rgba(0, 0, 0, 0.3)";

                    div.addEventListener("mouseenter", () => {
                        div.style.border = "1px solid green";
                        div.style.cursor = "pointer";
                    });

                    div.addEventListener("mouseleave", () => {
                        div.style.border = "1px solid #ccc"; // Reset to original
                    });

                    div.title = `${crop.crop} sowing month`;
                } else if (cell === "harvest") {
                    div.innerText = "🌾";
                      div.addEventListener("mouseenter", () => {
                        div.style.border = "1px solid yellow";
                        div.style.cursor = "pointer";
                    });

                    div.addEventListener("mouseleave", () => {
                        div.style.border = "1px solid #ccc"; // Reset to original
                    });
                     
                    div.style.transition = "box-shadow 0.3s ease";
                    div.style.boxShadow = "0px 4px 6px rgba(0, 0, 0, 0.3)";

                    div.title = `${crop.crop} harvesting month`;
                } else if (cell === "grow") {
                    div.innerText = "🟩";
                    div.style.transition = "box-shadow 0.3s ease";
                    div.style.boxShadow = "0px 4px 6px rgba(0, 0, 0, 0.3)";

                    div.title = `${crop.crop} growing period`;
                }
            }

            calendar.appendChild(div);
        });
    });
}

document.getElementById("cropSelect").addEventListener("change", function () {
    const selectedCrop = this.value;
    renderCalendar(selectedCrop);
});

// Initial render
renderCalendar();
