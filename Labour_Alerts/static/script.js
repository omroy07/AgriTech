document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.content');
    const postJobBtn = document.getElementById('postJobBtn');
    const postedJobsContainer = document.getElementById('postedJobs');
    const jobAlertsContainer = document.getElementById('dynamicJobAlerts');

    // Load Jobs from LocalStorage on Page Load
    const savedJobs = JSON.parse(localStorage.getItem('jobs')) || [];
    savedJobs.forEach(job => renderJob(job));

    // Tab Switching Logic
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // Post Job Button Click Handler
    postJobBtn.addEventListener('click', () => {
        const workType = document.getElementById('workType').value;
        const peopleCount = document.getElementById('peopleCount').value.trim();
        const date = document.getElementById('date').value;
        const village = document.getElementById('village').value.trim();
        const location = document.getElementById('location').value.trim();
        const address = document.getElementById('address').value.trim();
        const wage = document.getElementById('wage').value.trim();
        const contact = document.getElementById('contact').value.trim();

        if (!workType || !peopleCount || !date || !village || !location || !wage || !contact) {
            alert('Please fill all mandatory fields!');
            return;
        }

        const job = {
            id: Date.now(),
            workType,
            peopleCount,
            date,
            village,
            location,
            address,
            wage,
            contact
        };

        // Save to LocalStorage
        savedJobs.push(job);
        localStorage.setItem('jobs', JSON.stringify(savedJobs));

        // Render Job Card and Alert
        renderJob(job);

        // Clear Form Inputs
        document.getElementById('workType').value = '';
        document.getElementById('peopleCount').value = '';
        document.getElementById('date').value = '';
        document.getElementById('village').value = '';
        document.getElementById('location').value = '';
        document.getElementById('address').value = '';
        document.getElementById('wage').value = '';
        document.getElementById('contact').value = '';
    });

    // Function to Render Job in Posted Jobs & Alerts
    function renderJob(job) {
        const addressLine = job.address ? `<p>Address: ${job.address}</p>` : '';

        // Posted Job Card
        const jobDiv = document.createElement('div');
        jobDiv.className = 'posted-job';
        jobDiv.dataset.jobId = job.id;
        jobDiv.innerHTML = `
      <h4>${job.workType} - ${job.peopleCount} Labourers Needed</h4>
      <p>Village: ${job.village}, ${job.location}</p>
      ${addressLine}
      <p>Date: ${job.date}</p>
      <p>Wage: ₹${job.wage} per day</p>
      <p>Contact: ${job.contact}</p>
      <button class="delete-btn">Remove</button>
    `;
        postedJobsContainer.appendChild(jobDiv);

        // Job Alert Card
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert-card';
        alertDiv.dataset.jobId = job.id;
        alertDiv.innerHTML = `
      <h4>Labour Requirement</h4>
      <p>${job.workType} - ${job.peopleCount} labourers needed at ${job.village}, ${job.location}${job.address ? ', ' + job.address : ''} on ${job.date}. Wage: ₹${job.wage}/day. Contact: ${job.contact}</p>
    `;
        jobAlertsContainer.appendChild(alertDiv);
    }

    // Delete Job Button Handler (Event Delegation)
    postedJobsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const jobDiv = e.target.closest('.posted-job');
            const jobId = jobDiv.dataset.jobId;

            // Remove from DOM
            jobDiv.remove();
            const alertDiv = document.querySelector(`.alert-card[data-job-id='${jobId}']`);
            if (alertDiv) alertDiv.remove();

            // Remove from LocalStorage
            const updatedJobs = savedJobs.filter(job => job.id != jobId);
            localStorage.setItem('jobs', JSON.stringify(updatedJobs));
            savedJobs.splice(0, savedJobs.length, ...updatedJobs); // Sync savedJobs array
        }
    });
});

function fetchNewsUpdates() {
    fetch('http://127.0.0.1:5000/news')
        .then(response => response.json())
        .then(data => {
            if (data && Array.isArray(data.results)) {
                // console.log(data);
                displayNews(data.results);
            } else {
                console.error("Invalid data format received:", data);
            }
        })
        .catch(error => {
            console.error('Error fetching news:', error);
        });
}


function displayNews(articles) {
    const newsList = document.getElementById('newsList');
    newsList.innerHTML = '';  // Clear previous news

    if (Array.isArray(articles)) {
        articles.forEach(article => {
            const newsCard = document.createElement('div');
            newsCard.className = 'alert-card';

            newsCard.innerHTML = `
            <h4>${article.title}</h4>
            <a class="news-link" href="${article.link}" target="_blank">Read Full Article</a>
    `;
            newsList.appendChild(newsCard);

        });
    } else {
        console.error('Expected articles to be an array, but got:', articles);
    }
}

// Call fetchNewsUpdates when Alerts Tab is clicked
document.querySelector('.tab[data-tab="alerts"]').addEventListener('click', () => {
    fetchNewsUpdates();
});

setInterval(fetchNewsUpdates, 300000); // Fetch news every 5 minutes
            // --- Cursor Trailing Effect ---
const container = document.getElementById('cursorTrail');
const circleCount = 12;
const circles = [];

let mouseX = 0;
let mouseY = 0;

// Create circles
for (let i = 0; i < circleCount; i++) {
    const circle = document.createElement('div');
    circle.classList.add('cursor-circle');
    container.appendChild(circle);
    circles.push({ el: circle, x: 0, y: 0 });
}

// Mouse move
document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

// Click effects
document.addEventListener('mousedown', () => {
    circles.forEach(c => c.el.classList.add('cursor-clicking'));
});
document.addEventListener('mouseup', () => {
    circles.forEach(c => c.el.classList.remove('cursor-clicking'));
});

// Hover effects on interactive elements
document.addEventListener('mouseover', (e) => {
    if (e.target.closest('a, button, .cta-button, .service-card, .shipment-card')) {
        circles.forEach(c => c.el.classList.add('cursor-hovering'));
    }
});
document.addEventListener('mouseout', (e) => {
    if (e.target.closest('a, button, .cta-button, .service-card, .shipment-card')) {
        circles.forEach(c => c.el.classList.remove('cursor-hovering'));
    }
});

// Animate trailing effect
function animateCursor() {
    let x = mouseX;
    let y = mouseY;

    circles.forEach((circle) => {
        circle.x += (x - circle.x) * 0.25;
        circle.y += (y - circle.y) * 0.25;

        circle.el.style.left = circle.x + 'px';
        circle.el.style.top = circle.y + 'px';

        x = circle.x;
        y = circle.y;
    });

    requestAnimationFrame(animateCursor);
}
animateCursor();