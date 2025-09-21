// Sample blog data
const blogPosts = [
    {
        id: 1,
        title: "How to Grow Organic Tomatoes: Step-by-Step Guide",
        category: "farming-tips",
        description: "Learn the complete process of growing healthy organic tomatoes from seed to harvest with expert tips and techniques.",
        image: "https://images.unsplash.com/photo-1592841200221-23d2d1aaa22d?w=400&h=250&fit=crop",
        content: `
            <h3>Getting Started with Organic Tomatoes</h3>
            <p>Growing organic tomatoes is one of the most rewarding experiences for any farmer or gardener. This comprehensive guide will walk you through every step of the process.</p>
            
            <h3>Soil Preparation</h3>
            <p>Start with well-draining soil with a pH between 6.0-6.8. Mix in organic compost 2-3 weeks before planting. The soil should be rich in organic matter and have good drainage to prevent root rot.</p>
            
            <h3>Seed Selection and Planting</h3>
            <ul>
                <li>Choose certified organic seeds</li>
                <li>Start seeds indoors 6-8 weeks before last frost</li>
                <li>Plant seeds 1/4 inch deep in seed trays</li>
                <li>Maintain temperature between 65-75°F</li>
                <li>Provide 12-16 hours of light daily</li>
            </ul>
            
            <h3>Transplanting and Care</h3>
            <p>Transplant seedlings outdoors when soil temperature reaches 60°F. Space plants 24-36 inches apart. Install stakes or cages at planting time to support growth.</p>
            
            <h3>Organic Pest Control</h3>
            <p>Use companion planting with basil, marigolds, and nasturtiums. Apply neem oil for aphids and use beneficial insects like ladybugs for natural pest control.</p>
        `
    },
    {
        id: 2,
        title: "Smart Farming with IoT Sensors: Complete Guide",
        category: "technology",
        description: "Discover how IoT sensors are revolutionizing agriculture with real-time monitoring and automated farming solutions.",
        image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400&h=250&fit=crop",
        content: `
            <h3>Introduction to IoT in Agriculture</h3>
            <p>Internet of Things (IoT) technology is transforming modern agriculture by providing real-time data and automated solutions for better crop management.</p>
            
            <h3>Key IoT Sensors for Farming</h3>
            <ul>
                <li><strong>Soil Moisture Sensors:</strong> Monitor water levels and optimize irrigation</li>
                <li><strong>Temperature & Humidity Sensors:</strong> Track environmental conditions</li>
                <li><strong>pH Sensors:</strong> Monitor soil acidity for optimal growth</li>
                <li><strong>Light Sensors:</strong> Measure photosynthetically active radiation</li>
                <li><strong>Weather Stations:</strong> Predict weather patterns and plan accordingly</li>
            </ul>
            
            <h3>Benefits of Smart Farming</h3>
            <p>IoT sensors provide 24/7 monitoring, reduce water usage by up to 30%, increase crop yields by 15-20%, and enable predictive maintenance of equipment.</p>
            
            <h3>Implementation Strategy</h3>
            <p>Start with basic soil sensors, expand to weather monitoring, integrate with mobile apps for remote monitoring, and analyze data for informed decision-making.</p>
        `
    },
    {
        id: 3,
        title: "Current Market Prices for Major Crops - September 2025",
        category: "market-trends",
        description: "Stay updated with the latest market prices for wheat, rice, corn, and other major crops across different regions.",
        image: "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400&h=250&fit=crop",
        content: `
            <h3>Market Analysis - September 2025</h3>
            <p>Current market trends show steady growth in grain prices due to favorable weather conditions and increased global demand.</p>
            
            <h3>Major Crop Prices (per quintal)</h3>
            <ul>
                <li><strong>Wheat:</strong> ₹2,250 - ₹2,400</li>
                <li><strong>Rice (Paddy):</strong> ₹1,950 - ₹2,100</li>
                <li><strong>Corn:</strong> ₹1,850 - ₹2,000</li>
                <li><strong>Soybeans:</strong> ₹4,200 - ₹4,500</li>
                <li><strong>Cotton:</strong> ₹6,800 - ₹7,200</li>
            </ul>
            
            <h3>Regional Variations</h3>
            <p>Northern states are experiencing higher prices due to transportation costs, while southern markets show stable pricing with good supply chains.</p>
            
            <h3>Price Forecast</h3>
            <p>Experts predict a 5-8% increase in crop prices over the next quarter due to festive season demand and export opportunities.</p>
        `
    },
    {
        id: 4,
        title: "Seasonal Farming Tips for Winter Crops",
        category: "farming-tips",
        description: "Essential guidelines for growing winter crops including wheat, peas, and mustard with maximum yield potential.",
        image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=250&fit=crop",
        content: `
            <h3>Winter Crop Planning</h3>
            <p>Winter season (Rabi) crops are crucial for maintaining year-round agricultural productivity. Proper planning ensures maximum yields.</p>
            
            <h3>Top Winter Crops</h3>
            <ul>
                <li><strong>Wheat:</strong> Plant in November, harvest in March-April</li>
                <li><strong>Barley:</strong> Drought-resistant, good for dry regions</li>
                <li><strong>Peas:</strong> Nitrogen-fixing, improves soil health</li>
                <li><strong>Mustard:</strong> Oil seed crop, ready in 90-120 days</li>
                <li><strong>Chickpeas:</strong> High protein content, market demand</li>
            </ul>
            
            <h3>Soil Preparation</h3>
            <p>Prepare fields after monsoon harvest. Add organic manure and ensure proper drainage to prevent waterlogging.</p>
            
            <h3>Irrigation Management</h3>
            <p>Winter crops require 3-4 irrigations. First irrigation 20-25 days after sowing, then at flowering and grain filling stages.</p>
        `
    },
    {
        id: 5,
        title: "Organic Farming: Benefits and Best Practices",
        category: "sustainability",
        description: "Explore the advantages of organic farming and learn sustainable practices that benefit both farmers and the environment.",
        image: "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=250&fit=crop",
        content: `
            <h3>Why Choose Organic Farming?</h3>
            <p>Organic farming promotes sustainable agriculture while producing healthier food and protecting environmental resources.</p>
            
            <h3>Key Benefits</h3>
            <ul>
                <li>Higher market prices (20-40% premium)</li>
                <li>Improved soil health and fertility</li>
                <li>Reduced chemical input costs</li>
                <li>Better water retention in soil</li>
                <li>Enhanced biodiversity on farms</li>
            </ul>
            
            <h3>Organic Practices</h3>
            <p>Use crop rotation, composting, biological pest control, and cover cropping to maintain soil health and prevent pest buildup naturally.</p>
            
            <h3>Certification Process</h3>
            <p>Contact certified agencies, maintain detailed records, undergo inspection, and follow organic standards for 2-3 years for full certification.</p>
        `
    },
    {
        id: 6,
        title: "Precision Agriculture: Technology That Saves Resources",
        category: "technology",
        description: "Learn how precision agriculture uses GPS, drones, and data analytics to optimize farming operations and reduce waste.",
        image: "https://images.unsplash.com/photo-1585314062604-1a357de8b000?w=400&h=250&fit=crop",
        content: `
            <h3>What is Precision Agriculture?</h3>
            <p>Precision agriculture uses technology to optimize field-level management regarding crop farming, ensuring precise application of inputs.</p>
            
            <h3>Core Technologies</h3>
            <ul>
                <li><strong>GPS Technology:</strong> Accurate field mapping and navigation</li>
                <li><strong>Variable Rate Technology:</strong> Apply inputs based on specific field needs</li>
                <li><strong>Drone Technology:</strong> Aerial monitoring and spraying</li>
                <li><strong>Soil Sampling:</strong> Detailed nutrient analysis</li>
                <li><strong>Yield Monitoring:</strong> Track productivity across fields</li>
            </ul>
            
            <h3>Resource Savings</h3>
            <p>Precision agriculture can reduce fertilizer use by 15-20%, decrease pesticide applications by 10-25%, and optimize water usage by up to 30%.</p>
            
            <h3>Return on Investment</h3>
            <p>Despite initial costs, farmers typically see ROI within 3-5 years through reduced input costs and increased yields.</p>
        `
    },
    {
        id: 7,
        title: "Digital Marketplace Success Story: Farmer Ramesh's Journey",
        category: "business",
        description: "Read how farmer Ramesh increased his income by 300% using digital platforms to sell directly to consumers.",
        image: "https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=400&h=250&fit=crop",
        content: `
            <h3>Meet Farmer Ramesh</h3>
            <p>Ramesh Kumar, a smallholder farmer from Punjab, transformed his farming business using digital marketplaces and direct-to-consumer sales.</p>
            
            <h3>The Challenge</h3>
            <p>Traditional middlemen were taking 40-50% margins, leaving Ramesh with minimal profits despite producing high-quality vegetables.</p>
            
            <h3>Digital Transformation</h3>
            <ul>
                <li>Started selling on local e-commerce platforms</li>
                <li>Created social media presence for his farm</li>
                <li>Implemented organic certification</li>
                <li>Developed direct delivery system</li>
                <li>Built customer relationships through transparency</li>
            </ul>
            
            <h3>Results Achieved</h3>
            <p>Within 2 years, Ramesh's income increased from ₹2 lakhs to ₹8 lakhs annually. He now supplies to 200+ regular customers and has expanded his farming area.</p>
            
            <h3>Key Lessons</h3>
            <p>Quality consistency, timely delivery, customer communication, and leveraging technology are crucial for digital marketplace success.</p>
        `
    },
    {
        id: 8,
        title: "Government Subsidies for Solar Pumps: Complete Guide",
        category: "business",
        description: "Understand various government schemes offering subsidies for solar irrigation systems and how to apply for them.",
        image: "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400&h=250&fit=crop",
        content: `
            <h3>Solar Pump Subsidy Schemes</h3>
            <p>Government offers substantial subsidies to promote solar-powered irrigation systems for sustainable farming.</p>
            
            <h3>Available Schemes</h3>
            <ul>
                <li><strong>PM-KUSUM Scheme:</strong> Up to 60% subsidy on solar pumps</li>
                <li><strong>State Solar Policies:</strong> Additional 20-30% state subsidies</li>
                <li><strong>Bank Loans:</strong> Low-interest financing options</li>
                <li><strong>NABARD Schemes:</strong> Special rural development funding</li>
            </ul>
            
            <h3>Eligibility Criteria</h3>
            <p>Farmers with agricultural land, valid electricity connection (for replacement), and documents proving land ownership are eligible.</p>
            
            <h3>Application Process</h3>
            <p>Apply through state nodal agency, submit required documents, get technical feasibility done, and complete installation through empaneled vendors.</p>
            
            <h3>Benefits</h3>
            <p>Reduced electricity bills, reliable irrigation, low maintenance costs, and 25-year warranty make solar pumps highly cost-effective.</p>
        `
    },
    {
        id: 9,
        title: "Eco-Friendly Pest Control Methods That Actually Work",
        category: "sustainability",
        description: "Discover natural and organic pest control solutions that protect crops without harming beneficial insects or soil health.",
        image: "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=250&fit=crop",
        content: `
            <h3>Natural Pest Management</h3>
            <p>Effective pest control doesn't require harmful chemicals. Natural methods can be equally effective while protecting the environment.</p>
            
            <h3>Biological Control Methods</h3>
            <ul>
                <li><strong>Beneficial Insects:</strong> Ladybugs, lacewings, predatory mites</li>
                <li><strong>Parasitic Wasps:</strong> Control caterpillars and aphids</li>
                <li><strong>Bacillus thuringiensis:</strong> Natural bacterial pesticide</li>
                <li><strong>Nematodes:</strong> Control soil-dwelling pests</li>
            </ul>
            
            <h3>Plant-Based Solutions</h3>
            <p>Neem oil, garlic spray, soap solutions, and essential oils provide effective pest deterrence without chemical residues.</p>
            
            <h3>Cultural Practices</h3>
            <p>Crop rotation, companion planting, trap crops, and maintaining field hygiene prevent pest buildup naturally.</p>
            
            <h3>Success Rates</h3>
            <p>Integrated pest management combining these methods shows 80-90% effectiveness while maintaining ecological balance.</p>
        `
    },
    {
        id: 10,
        title: "Water Management Techniques for Drought-Prone Areas",
        category: "farming-tips",
        description: "Learn innovative water conservation methods and drought-resistant farming techniques for sustainable agriculture.",
        image: "https://images.unsplash.com/photo-1601134467661-3d775b999c8b?w=400&h=250&fit=crop",
        content: `
            <h3>Water Scarcity Solutions</h3>
            <p>Effective water management is crucial for farming in drought-prone regions. Smart techniques can maximize every drop of available water.</p>
            
            <h3>Water Conservation Methods</h3>
            <ul>
                <li><strong>Drip Irrigation:</strong> 40-60% water savings compared to flood irrigation</li>
                <li><strong>Mulching:</strong> Reduces evaporation by 50-70%</li>
                <li><strong>Rainwater Harvesting:</strong> Store monsoon water for dry periods</li>
                <li><strong>Contour Farming:</strong> Prevent water runoff on slopes</li>
                <li><strong>Cover Crops:</strong> Improve soil water retention</li>
            </ul>
            
            <h3>Drought-Resistant Crops</h3>
            <p>Choose varieties like pearl millet, sorghum, drought-tolerant rice, and hardy legumes that require minimal water.</p>
            
            <h3>Soil Management</h3>
            <p>Add organic matter to improve water retention capacity. Avoid over-tillage that increases water evaporation from soil surface.</p>
            
            <h3>Technology Integration</h3>
            <p>Use soil moisture sensors, weather-based irrigation scheduling, and mobile apps for efficient water management.</p>
        `
    }
];

// Global variables
let currentPage = 0;
const postsPerPage = 6;
let filteredPosts = [...blogPosts];
let currentCategory = 'all';
let searchQuery = '';

// DOM elements
const blogGrid = document.getElementById('blogGrid');
const searchInput = document.getElementById('searchInput');
const loadMoreBtn = document.getElementById('loadMoreBtn');
const modal = document.getElementById('blogModal');
const filterButtons = document.querySelectorAll('.filter-btn');

// Initialize the blog
document.addEventListener('DOMContentLoaded', function() {
    displayPosts();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    searchInput.addEventListener('input', function() {
        searchQuery = this.value.toLowerCase();
        filterPosts();
    });

    // Filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            currentCategory = this.dataset.category;
            filterPosts();
        });
    });

    // Load more button
    loadMoreBtn.addEventListener('click', loadMorePosts);

    // Modal functionality
    const closeModal = document.querySelector('.close');
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
}

// Filter posts based on search and category
function filterPosts() {
    filteredPosts = blogPosts.filter(post => {
        const matchesSearch = post.title.toLowerCase().includes(searchQuery) || 
                            post.description.toLowerCase().includes(searchQuery) ||
                            post.category.toLowerCase().includes(searchQuery);
        const matchesCategory = currentCategory === 'all' || post.category === currentCategory;
        
        return matchesSearch && matchesCategory;
    });

    currentPage = 0;
    blogGrid.innerHTML = '';
    displayPosts();
}

// Display posts
function displayPosts() {
    const startIndex = currentPage * postsPerPage;
    const endIndex = startIndex + postsPerPage;
    const postsToShow = filteredPosts.slice(startIndex, endIndex);

    if (postsToShow.length === 0 && startIndex === 0) {
        blogGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #666; font-size: 1.2rem;">No posts found matching your criteria.</div>';
        loadMoreBtn.style.display = 'none';
        return;
    }

    postsToShow.forEach(post => {
        const postElement = createPostElement(post);
        blogGrid.appendChild(postElement);
    });

    // Update load more button
    if (endIndex >= filteredPosts.length) {
        loadMoreBtn.style.display = 'none';
    } else {
        loadMoreBtn.style.display = 'inline-block';
    }
}

// Create post element
function createPostElement(post) {
    const postDiv = document.createElement('div');
    postDiv.className = 'blog-card';
    postDiv.innerHTML = `
        <img src="${post.image}" alt="${post.title}" onerror="this.src='https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&h=250&fit=crop'">
        <div class="card-content">
            <span class="card-category">${post.category.replace('-', ' ')}</span>
            <h3 class="card-title">${post.title}</h3>
            <p class="card-description">${post.description}</p>
            <button class="read-more-btn" onclick="openModal(${post.id})">Read More</button>
        </div>
    `;

    return postDiv;
}

// Load more posts
function loadMorePosts() {
    currentPage++;
    displayPosts();
}

// Open modal with post content
function openModal(postId) {
    const post = blogPosts.find(p => p.id === postId);
    if (!post) return;

    document.getElementById('modalTitle').textContent = post.title;
    document.getElementById('modalCategory').textContent = post.category.replace('-', ' ');
    document.getElementById('modalImage').src = post.image;
    document.getElementById('modalContent').innerHTML = post.content;

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Utility functions for smooth animations
function animateCards() {
    const cards = document.querySelectorAll('.blog-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Call animation after posts are loaded
function displayPostsWithAnimation() {
    displayPosts();
    setTimeout(animateCards, 100);
}

// Update the filter function to use animation
function filterPosts() {
    filteredPosts = blogPosts.filter(post => {
        const matchesSearch = post.title.toLowerCase().includes(searchQuery) || 
                            post.description.toLowerCase().includes(searchQuery) ||
                            post.category.toLowerCase().includes(searchQuery);
        const matchesCategory = currentCategory === 'all' || post.category === currentCategory;
        
        return matchesSearch && matchesCategory;
    });

    currentPage = 0;
    blogGrid.innerHTML = '';
    displayPostsWithAnimation();
}


// Thats All Folks!