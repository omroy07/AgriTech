// Agricultural Schemes Database
const schemesDatabase = [
    // National Schemes - Credit & Finance
    {
        id: 1,
        title: "Kisan Credit Card (KCC)",
        category: "credit",
        state: "national",
        gender: "all",
        description: "Provides timely credit support for agriculture and allied activities including crop production, maintenance of farm assets and consumption requirements.",
        benefits: [
            "Credit limit up to ₹3 lakhs without collateral",
            "Simple documentation and quick processing",
            "Flexible repayment terms",
            "Interest subvention up to 3%"
        ],
        updated: "2024-12-15",
        applyUrl: "#"
    },
    {
        id: 2,
        title: "NABARD Refinance Scheme",
        category: "credit",
        state: "national", 
        gender: "all",
        description: "Provides refinance to banks for agricultural and rural development activities through various schemes.",
        benefits: [
            "Low-interest refinance to banks",
            "Support for farm mechanization",
            "Infrastructure development funding",
            "Rural non-farm sector support"
        ],
        updated: "2024-11-20",
        applyUrl: "#"
    },

    // National Schemes - Subsidy
    {
        id: 3,
        title: "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        category: "subsidy",
        state: "national",
        gender: "all", 
        description: "Direct income support to farmers with landholding up to 2 hectares to supplement financial needs.",
        benefits: [
            "₹6,000 per year in three installments",
            "Direct bank transfer",
            "No income tax for beneficiaries",
            "Simple enrollment process"
        ],
        updated: "2024-12-01",
        applyUrl: "#"
    },
    {
        id: 4,
        title: "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        category: "insurance",
        state: "national",
        gender: "all",
        description: "Comprehensive crop insurance scheme covering pre-sowing to post-harvest losses due to natural calamities.",
        benefits: [
            "Premium subsidy up to 50% for farmers",
            "Coverage for all stages of crop cycle",
            "Quick claim settlement through technology",
            "Coverage for localized risks and post-harvest losses"
        ],
        updated: "2024-12-10",
        applyUrl: "#"
    },

    // Women-Specific Schemes
    {
        id: 5,
        title: "Mahila Kisan Sashaktikaran Pariyojana (MKSP)",
        category: "women",
        state: "national",
        gender: "female",
        description: "Women-centric approach to enhance opportunities for women in agriculture through capacity building and empowerment.",
        benefits: [
            "Skill development programs for women farmers",
            "Formation of women Self Help Groups",
            "Access to credit and financial services",
            "Training on improved agricultural practices"
        ],
        updated: "2024-11-25",
        applyUrl: "#"
    },
    {
        id: 6,
        title: "Women Farmer Special Provisions under NMAET",
        category: "women",
        state: "national",
        gender: "female",
        description: "Special provisions for women farmers under National Mission on Agricultural Extension & Technology.",
        benefits: [
            "Minimum 30% allocation for women farmers",
            "Priority in farm mechanization schemes",
            "Women-friendly farm equipment subsidies",
            "Training programs exclusively for women"
        ],
        updated: "2024-12-05",
        applyUrl: "#"
    },

    // Technology & Equipment
    {
        id: 7,
        title: "Sub-Mission on Agricultural Mechanization (SMAM)",
        category: "technology",
        state: "national",
        gender: "all",
        description: "Promotes farm mechanization through financial assistance for purchase of agricultural machinery and equipment.",
        benefits: [
            "40-50% subsidy on farm equipment",
            "Custom Hiring Centers support",
            "Hi-tech hubs and farm machinery banks",
            "Testing and certification of farm equipment"
        ],
        updated: "2024-11-30",
        applyUrl: "#"
    },
    {
        id: 8,
        title: "Mission for Integrated Development of Horticulture (MIDH)",
        category: "subsidy",
        state: "national", 
        gender: "all",
        description: "Holistic development of horticulture sector covering fruits, vegetables, root & tuber crops, mushrooms, spices, flowers, aromatic plants, coconut and cashew.",
        benefits: [
            "50% subsidy for protected cultivation",
            "Support for post-harvest infrastructure",
            "Organic farming promotion",
            "Market infrastructure development"
        ],
        updated: "2024-12-08",
        applyUrl: "#"
    },

    // Organic Farming
    {
        id: 9,
        title: "Paramparagat Krishi Vikas Yojana (PKVY)",
        category: "organic",
        state: "national",
        gender: "all",
        description: "Promotes organic farming through cluster approach and PGS certification to improve soil health and organic matter content.",
        benefits: [
            "₹50,000 per hectare over 3 years",
            "Organic certification support",
            "Cluster formation for 50 farmers",
            "Market linkage assistance"
        ],
        updated: "2024-11-28",
        applyUrl: "#"
    },

    // Youth & Startup Schemes
    {
        id: 10,
        title: "ACABC (Agri-Clinic and Agri-Business Centres)",
        category: "youth",
        state: "national",
        gender: "all",
        description: "Provides technical support and financial assistance to agriculture graduates for establishing agri-clinics and agri-business centers.",
        benefits: [
            "Composite loan up to ₹25 lakhs",
            "25% back-ended subsidy",
            "Training and hand-holding support",
            "Market linkage facilitation"
        ],
        updated: "2024-12-01",
        applyUrl: "#"
    },
    {
        id: 11,
        title: "Stand Up India Scheme (Agriculture)",
        category: "youth",
        state: "national",
        gender: "all",
        description: "Facilitates bank loans between ₹10 lakh to ₹1 crore for agriculture-based enterprises, especially for SC/ST and women entrepreneurs.",
        benefits: [
            "Loans from ₹10 lakh to ₹1 crore",
            "7 years repayment period with 18 months moratorium",
            "Lower interest rates",
            "Handholding support for 2 years"
        ],
        updated: "2024-11-22",
        applyUrl: "#"
    },

    // State Specific Schemes - Maharashtra
    {
        id: 12,
        title: "Jalyukt Shivar Abhiyan",
        category: "subsidy",
        state: "maharashtra",
        gender: "all",
        description: "Maharashtra's flagship program for drought-proofing villages through water conservation and watershed management.",
        benefits: [
            "Free water conservation structures",
            "Watershed development programs",
            "Community participation in water management",
            "Sustainable agriculture practices"
        ],
        updated: "2024-12-03",
        applyUrl: "#"
    },
    {
        id: 13,
        title: "Maharashtra State Women Agriculture Development Mission",
        category: "women",
        state: "maharashtra",
        gender: "female",
        description: "Specific focus on empowering women farmers through capacity building and financial assistance.",
        benefits: [
            "Training on modern farming techniques",
            "Formation of women farmer groups",
            "Priority in government schemes",
            "Financial assistance for farm activities"
        ],
        updated: "2024-11-18",
        applyUrl: "#"
    },

    // State Specific - Punjab
    {
        id: 14,
        title: "Punjab Crop Diversification Program",
        category: "subsidy",
        state: "punjab",
        gender: "all",
        description: "Incentivizes farmers to shift from rice-wheat cropping system to alternative crops to preserve groundwater.",
        benefits: [
            "₹17,500 per hectare incentive",
            "Free seeds for alternative crops",
            "Assured procurement of alternative crops",
            "Technical guidance and support"
        ],
        updated: "2024-12-12",
        applyUrl: "#"
    },

    // State Specific - Karnataka
    {
        id: 15,
        title: "Raitha Samparka Centers (RSC)",
        category: "training",
        state: "karnataka",
        gender: "all",
        description: "One-stop service centers providing agricultural services, inputs, and extension support to farmers.",
        benefits: [
            "Soil testing services",
            "Quality input supplies",
            "Expert advisory services",
            "Market information and linkages"
        ],
        updated: "2024-11-29",
        applyUrl: "#"
    },
    {
        id: 16,
        title: "Karnataka Mahila Kisan Empowerment",
        category: "women", 
        state: "karnataka",
        gender: "female",
        description: "Empowers women farmers through skill development, financial support, and leadership training.",
        benefits: [
            "Leadership development programs",
            "Access to credit without collateral",
            "Training on value addition techniques",
            "Market linkage support for women groups"
        ],
        updated: "2024-12-02",
        applyUrl: "#"
    },

    // State Specific - Uttar Pradesh
    {
        id: 17,
        title: "UP Kisan Kalyan Mission",
        category: "subsidy",
        state: "uttar-pradesh",
        gender: "all",
        description: "Comprehensive program for farmer welfare including input subsidies, crop insurance, and infrastructure development.",
        benefits: [
            "Enhanced input subsidies",
            "Free electricity for irrigation",
            "Crop insurance premium support",
            "Modern storage facilities"
        ],
        updated: "2024-11-26",
        applyUrl: "#"
    },

    // State Specific - Tamil Nadu  
    {
        id: 18,
        title: "Tamil Nadu Comprehensive Crop Insurance Scheme",
        category: "insurance",
        state: "tamil-nadu",
        gender: "all", 
        description: "State-sponsored crop insurance providing comprehensive coverage against natural calamities and pests.",
        benefits: [
            "Higher sum insured than PMFBY",
            "Quick claim settlement",
            "Coverage for multiple risks",
            "Subsidized premium rates"
        ],
        updated: "2024-12-07",
        applyUrl: "#"
    },
    {
        id: 19,
        title: "Tamil Nadu Women Farmers Collectivization",
        category: "women",
        state: "tamil-nadu", 
        gender: "female",
        description: "Promotes collectivization of women farmers into groups for better access to resources and markets.",
        benefits: [
            "Formation of women farmer collectives",
            "Bulk procurement of inputs",
            "Collective marketing advantages",
            "Training on group management"
        ],
        updated: "2024-11-20",
        applyUrl: "#"
    },

    // State Specific - West Bengal
    {
        id: 20,
        title: "Krishak Bandhu Scheme",
        category: "subsidy",
        state: "west-bengal",
        gender: "all",
        description: "Financial assistance to farmers for cultivation support and life insurance coverage.",
        benefits: [
            "₹5,000 per hectare cultivation support",
            "₹2 lakh life insurance coverage",
            "Support for both seasons",
            "Direct benefit transfer"
        ],
        updated: "2024-12-04",
        applyUrl: "#"
    },

    // State Specific - Rajasthan
    {
        id: 21,
        title: "Rajasthan Mukhyamantri Kisan Mitra Urja Yojana",
        category: "subsidy",
        state: "rajasthan",
        gender: "all",
        description: "Electricity bill subsidy for agricultural connections to reduce farming costs.",
        benefits: [
            "₹12,000 annual electricity subsidy",
            "Metered agriculture connections",
            "Reliable power supply",
            "Reduced farming costs"
        ],
        updated: "2024-11-24",
        applyUrl: "#"
    },

    // Training & Skill Development
    {
        id: 22,
        title: "Agricultural Technology Management Agency (ATMA)",
        category: "training",
        state: "national",
        gender: "all",
        description: "Decentralized extension system providing integrated agricultural extension services at district level.",
        benefits: [
            "Farmer training programs",
            "Demonstration plots",
            "Technology dissemination",
            "Farmer-scientist interaction"
        ],
        updated: "2024-12-06",
        applyUrl: "#"
    },
    {
        id: 23,
        title: "Skill Development for Women in Agriculture",
        category: "training",
        state: "national",
        gender: "female",
        description: "Specialized skill development programs focusing on enhancing technical skills of women in agriculture.",
        benefits: [
            "Technical skill enhancement",
            "Entrepreneurship development", 
            "Modern farming technique training",
            "Certification and placement support"
        ],
        updated: "2024-11-27",
        applyUrl: "#"
    },

    // More State Specific Schemes
    {
        id: 24,
        title: "Haryana Agriculture Infrastructure Development",
        category: "subsidy",
        state: "haryana",
        gender: "all",
        description: "Infrastructure development program for modernizing agriculture in Haryana through technology adoption.",
        benefits: [
            "Subsidized farm equipment",
            "Cold storage facility support",
            "Market infrastructure development",
            "Technology adoption incentives"
        ],
        updated: "2024-12-01",
        applyUrl: "#"
    },
    {
        id: 25,
        title: "Gujarat Soil Health Management",
        category: "organic",
        state: "gujarat",
        gender: "all",
        description: "Comprehensive soil health improvement program through organic farming and sustainable practices.",
        benefits: [
            "Free soil testing",
            "Organic fertilizer subsidies",
            "Soil health card distribution",
            "Training on sustainable practices"
        ],
        updated: "2024-11-23",
        applyUrl: "#"
    },

    // Additional schemes for better coverage
    {
        id: 26,
        title: "National Food Security Mission (NFSM)",
        category: "subsidy",
        state: "national",
        gender: "all",
        description: "Aims to increase production and productivity of rice, wheat, pulses, and coarse cereals through area expansion and productivity enhancement.",
        benefits: [
            "Certified seed distribution",
            "Integrated nutrient management",
            "Resource conservation technology",
            "Capacity building of farmers"
        ],
        updated: "2024-12-11",
        applyUrl: "#"
    },
    {
        id: 27,
        title: "National Mission on Oilseeds and Oil Palm (NMOOP)",
        category: "subsidy",
        state: "national",
        gender: "all",
        description: "Comprehensive scheme to increase production and productivity of oilseeds and oil palm in the country.",
        benefits: [
            "Quality seed distribution",
            "Integrated pest management",
            "Processing and value addition support",
            "Market linkage assistance"
        ],
        updated: "2024-11-15",
        applyUrl: "#"
    },
    {
        id: 28,
        title: "Andhra Pradesh YSR Rythu Bharosa",
        category: "subsidy",
        state: "andhra-pradesh",
        gender: "all",
        description: "Direct cash transfer scheme providing financial assistance to farmers for agricultural activities.",
        benefits: [
            "₹13,500 per year for farming families",
            "Direct benefit transfer",
            "Input cost support",
            "Zero-interest loans"
        ],
        updated: "2024-12-09",
        applyUrl: "#"
    },
    {
        id: 29,
        title: "Kerala Organic Farming Mission",
        category: "organic",
        state: "kerala",
        gender: "all",
        description: "State-wide organic farming promotion program with focus on sustainable agriculture practices.",
        benefits: [
            "Organic certification support",
            "Bio-input production training",
            "Market premium for organic products",
            "Technical guidance and monitoring"
        ],
        updated: "2024-11-30",
        applyUrl: "#"
    },
    {
        id: 30,
        title: "Telangana Rythu Bandhu Scheme",
        category: "subsidy",
        state: "telangana",
        gender: "all",
        description: "Investment support scheme providing financial assistance to farmers for agricultural inputs.",
        benefits: [
            "₹10,000 per acre per year",
            "Direct payment to farmer accounts",
            "Support for both seasons",
            "No conditions or restrictions"
        ],
        updated: "2024-12-13",
        applyUrl: "#"
    },
    // State Specific - Assam
    {
        id: 31,
        title: "Mukhya Mantri Krishi Saajuli Yojana",
        category: "technology",
        state: "assam",
        gender: "all",
        description: "Financial assistance to farmers for procuring farm tools and implements to promote scientific cultivation.",
        benefits: [
            "Financial aid of ₹5,000 per farmer",
            "Direct Benefit Transfer (DBT)",
            "Focus on small and marginal farmers",
            "Promotes farm mechanization"
        ],
        updated: "2024-12-10",
        applyUrl: "#"
    },

    // State Specific - Bihar
    {
        id: 32,
        title: "Bihar Rajya Fasal Sahayata Yojana",
        category: "insurance",
        state: "bihar",
        gender: "all",
        description: "A crop assistance scheme that replaces traditional insurance, providing financial aid to farmers in case of crop damage.",
        benefits: [
            "₹7,500/hectare for up to 20% loss",
            "₹10,000/hectare for >20% loss",
            "No premium required from farmers",
            "Coverage for both Rabi and Kharif crops"
        ],
        updated: "2024-11-28",
        applyUrl: "#"
    },

    // State Specific - Chhattisgarh
    {
        id: 33,
        title: "Rajiv Gandhi Kisan Nyay Yojana",
        category: "subsidy",
        state: "chhattisgarh",
        gender: "all",
        description: "Income support scheme encouraging farmers to cultivate crops other than paddy and ensuring fair prices.",
        benefits: [
            "Input subsidy up to ₹10,000 per acre",
            "Support for crop diversification",
            "Direct cash transfer to bank accounts",
            "Coverage for paddy, maize, and sugarcane"
        ],
        updated: "2024-12-15",
        applyUrl: "#"
    },

    // State Specific - Madhya Pradesh
    {
        id: 34,
        title: "Mukhyamantri Kisan Kalyan Yojana",
        category: "subsidy",
        state: "madhya-pradesh",
        gender: "all",
        description: "State-level income support scheme that supplements the central PM-KISAN yojana.",
        benefits: [
            "Additional ₹4,000 per year",
            "Paid in two installments of ₹2,000",
            "Synced with PM-KISAN database",
            "Total benefit (Central + State): ₹10,000/year"
        ],
        updated: "2024-12-05",
        applyUrl: "#"
    },

    // State Specific - Odisha
    {
        id: 35,
        title: "KALIA Scheme (Krushak Assistance for Livelihood and Income Augmentation)",
        category: "subsidy",
        state: "odisha",
        gender: "all",
        description: "Comprehensive welfare package for farmers, sharecroppers, and landless agricultural laborers.",
        benefits: [
            "₹25,000 financial assistance over 5 seasons",
            "Support for landless agricultural households",
            "Life insurance cover of ₹2 lakh",
            "Interest-free crop loans"
        ],
        updated: "2024-11-30",
        applyUrl: "#"
    }
];

// Global variables
let filteredSchemes = [...schemesDatabase];
let currentView = 'card';
let currentGenderFilter = 'all';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const stateFilter = document.getElementById('stateFilter'); 
const sortFilter = document.getElementById('sortFilter');
const schemesContainer = document.getElementById('schemesContainer');
const schemeCount = document.getElementById('schemeCount');
const loadingState = document.getElementById('loadingState');
const noResults = document.getElementById('noResults');
const lastUpdated = document.getElementById('lastUpdated');

// Theme Management
let isDarkMode = localStorage.getItem('darkMode') === 'true';

function toggleTheme() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode', isDarkMode);
    localStorage.setItem('darkMode', isDarkMode);
    
    const themeBtn = document.querySelector('.theme-btn');
    const themeIcon = document.querySelector('.theme-icon');
    
    if (isDarkMode) {
        themeIcon.textContent = '🌙';
        themeBtn.childNodes[1].textContent = ' Dark Mode';
    } else {
        themeIcon.textContent = '🌞';
        themeBtn.childNodes[1].textContent = ' Light Mode';
    }
}

// Initialize theme
function initializeTheme() {
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        const themeIcon = document.querySelector('.theme-icon');
        const themeBtn = document.querySelector('.theme-btn');
        if (themeIcon && themeBtn) {
            themeIcon.textContent = '🌙';
            themeBtn.childNodes[1].textContent = ' Dark Mode';
        }
    }
}

// Filter by gender
function filterByGender(gender) {
    currentGenderFilter = gender;
    
    // Update active button
    document.querySelectorAll('.gender-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`[data-gender="${gender}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    applyFilters();
}

// Toggle view
function toggleView(view) {
    currentView = view;
    schemesContainer.className = `schemes-container ${view}-view`;
    
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`[data-view="${view}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    renderSchemes();
}

// Apply all filters
function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase();
    const categoryValue = categoryFilter.value;
    const stateValue = stateFilter.value;
    
    filteredSchemes = schemesDatabase.filter(scheme => {
        const matchesSearch = !searchTerm || 
            scheme.title.toLowerCase().includes(searchTerm) ||
            scheme.description.toLowerCase().includes(searchTerm) ||
            scheme.benefits.some(benefit => benefit.toLowerCase().includes(searchTerm));
            
        const matchesCategory = !categoryValue || scheme.category === categoryValue;
        const matchesState = !stateValue || scheme.state === stateValue;
        const matchesGender = currentGenderFilter === 'all' || 
            scheme.gender === 'all' || scheme.gender === currentGenderFilter;
        
        return matchesSearch && matchesCategory && matchesState && matchesGender;
    });
    
    sortSchemes();
    renderSchemes();
}

// Sort schemes
function sortSchemes() {
    const sortValue = sortFilter.value;
    
    filteredSchemes.sort((a, b) => {
        switch (sortValue) {
            case 'name':
                return a.title.localeCompare(b.title);
            case 'category':
                return a.category.localeCompare(b.category);
            case 'state':
                return a.state.localeCompare(b.state);
            default:
                return 0;
        }
    });
}

// Render schemes
function renderSchemes() {
    // Hide loading state
    if (loadingState) {
        loadingState.style.display = 'none';
    }
    
    // Update scheme count
    if (schemeCount) {
        schemeCount.textContent = `(${filteredSchemes.length} schemes found)`;
    }
    
    if (filteredSchemes.length === 0) {
        if (schemesContainer) {
            schemesContainer.style.display = 'none';
        }
        if (noResults) {
            noResults.style.display = 'block';
        }
        return;
    }
    
    if (noResults) {
        noResults.style.display = 'none';
    }
    if (schemesContainer) {
        schemesContainer.style.display = 'grid';
    }
    
    if (!schemesContainer) return;
    
    schemesContainer.innerHTML = filteredSchemes.map(scheme => {
        const categoryNames = {
            'credit': 'Credit & Finance',
            'subsidy': 'Subsidy Schemes', 
            'insurance': 'Insurance',
            'technology': 'Technology & Equipment',
            'training': 'Training & Development',
            'women': 'Women Specific',
            'youth': 'Youth & Startup',
            'organic': 'Organic Farming'
        };
        
        const stateNames = {
            'national': 'National',
            'andhra-pradesh': 'Andhra Pradesh',
            'assam': 'Assam',
            'bihar': 'Bihar', 
            'chhattisgarh': 'Chhattisgarh',
            'gujarat': 'Gujarat',
            'haryana': 'Haryana',
            'karnataka': 'Karnataka',
            'kerala': 'Kerala',
            'madhya-pradesh': 'Madhya Pradesh',
            'maharashtra': 'Maharashtra',
            'odisha': 'Odisha',
            'punjab': 'Punjab',
            'rajasthan': 'Rajasthan',
            'tamil-nadu': 'Tamil Nadu',
            'telangana': 'Telangana',
            'uttar-pradesh': 'Uttar Pradesh',
            'west-bengal': 'West Bengal'
        };
        
        const genderDisplay = scheme.gender === 'all' ? 'All Farmers' : 
                            scheme.gender === 'male' ? 'Male Farmers' : 'Women Farmers';
        
        return `
            <div class="scheme-card" data-id="${scheme.id}">
                <div class="scheme-header">
                    <h3 class="scheme-title">${scheme.title}</h3>
                    <div class="scheme-meta">
                        <span class="scheme-tag category">${categoryNames[scheme.category]}</span>
                        <span class="scheme-tag state">${stateNames[scheme.state]}</span>
                        <span class="scheme-tag gender">${genderDisplay}</span>
                    </div>
                </div>
                
                <div class="scheme-body">
                    <p class="scheme-description">${scheme.description}</p>
                    
                    <div class="scheme-benefits">
                        <h4>Key Benefits:</h4>
                        <ul class="benefits-list">
                            ${scheme.benefits.slice(0, 3).map(benefit => 
                                `<li>${benefit}</li>`
                            ).join('')}
                            ${scheme.benefits.length > 3 ? 
                                `<li><strong>+${scheme.benefits.length - 3} more benefits</strong></li>` : ''
                            }
                        </ul>
                    </div>
                </div>
                
                <div class="scheme-footer">
                    <a href="${scheme.applyUrl}" class="apply-btn" onclick="handleApply('${scheme.title}'); return false;">
                        Apply Now
                    </a>
                    <span class="scheme-updated">Updated: ${formatDate(scheme.updated)}</span>
                </div>
            </div>
        `;
    }).join('');
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short', 
        day: 'numeric'
    });
}

// Handle apply button click
function handleApply(schemeTitle) {
    alert(`Redirecting to application form for: ${schemeTitle}\n\nNote: This is a demo. In a real application, this would redirect to the official government portal.`);
}

// Reset all filters
function resetFilters() {
    if (searchInput) searchInput.value = '';
    if (categoryFilter) categoryFilter.selectedIndex = 0;
    if (stateFilter) stateFilter.selectedIndex = 0;
    if (sortFilter) sortFilter.selectedIndex = 0;
    
    // Reset gender filter to 'all'
    filterByGender('all');
}

// Initialize the application
function initialize() {
    // Set last updated date
    if (lastUpdated) {
        lastUpdated.textContent = new Date().toLocaleDateString('en-IN');
    }
    
    // Initialize theme
    initializeTheme();
    
    // Add event listeners
    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
    if (categoryFilter) {
        categoryFilter.addEventListener('change', applyFilters);
    }
    if (stateFilter) {
        stateFilter.addEventListener('change', applyFilters);
    }
    if (sortFilter) {
        sortFilter.addEventListener('change', applyFilters);
    }
    
    // Initial render with delay to show loading state
    setTimeout(() => {
        applyFilters();
    }, 500);
}

// Debounce function for search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    // ESC key to reset filters
    if (e.key === 'Escape') {
        resetFilters();
    }
    
    // F key to focus search (when not in input)
    if (e.key === 'f' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // T key to toggle theme
    if (e.key === 't' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        toggleTheme();
    }
});

// Add smooth scrolling for better UX
function smoothScrollTo(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Performance optimization: Intersection Observer for lazy loading
if ('IntersectionObserver' in window) {
    const observerOptions = {
        root: null,
        rootMargin: '50px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe scheme cards when they're rendered
    function observeSchemeCards() {
        const cards = document.querySelectorAll('.scheme-card');
        cards.forEach(card => {
            observer.observe(card);
        });
    }
    
    // Call this after rendering schemes
    setTimeout(observeSchemeCards, 600);
}

// Error handling for missing elements
function safeQuerySelector(selector) {
    const element = document.querySelector(selector);
    if (!element) {
        console.warn(`Element not found: ${selector}`);
    }
    return element;
}

// Analytics tracking (placeholder for real implementation)
function trackUserAction(action, data) {
    console.log('User Action:', action, data);
    // In real implementation, this would send data to analytics service
}

// Track filter usage
function trackFilterUsage() {
    const filters = {
        search: searchInput?.value || '',
        category: categoryFilter?.value || 'all',
        state: stateFilter?.value || 'all',
        gender: currentGenderFilter,
        view: currentView
    };
    trackUserAction('filter_applied', filters);
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', initialize);

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        schemesDatabase,
        applyFilters,
        filterByGender,
        toggleTheme,
        resetFilters,
        formatDate
    };
}