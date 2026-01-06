/**
 * AgriTech Utility Functions
 * Comprehensive JavaScript utilities for the AgriTech frontend
 * @module js/agri-helpers
 */

// ============================================================
// DATE AND TIME UTILITIES
// ============================================================

/**
 * Format date for display
 * @param {Date|string} date - Date to format
 * @param {string} format - Format type: 'short', 'long', 'iso', 'relative'
 * @returns {string} Formatted date string
 */
function formatDate(date, format = 'short') {
    const d = new Date(date);
    if (isNaN(d.getTime())) return 'Invalid Date';

    const options = {
        short: { day: '2-digit', month: 'short', year: 'numeric' },
        long: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' },
        iso: null,
        relative: null
    };

    if (format === 'iso') {
        return d.toISOString().split('T')[0];
    }

    if (format === 'relative') {
        return getRelativeTime(d);
    }

    return d.toLocaleDateString('en-IN', options[format] || options.short);
}

/**
 * Get relative time string (e.g., "2 hours ago", "in 3 days")
 * @param {Date} date - Date to compare
 * @returns {string} Relative time string
 */
function getRelativeTime(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.abs(diff / 1000);
    const minutes = seconds / 60;
    const hours = minutes / 60;
    const days = hours / 24;
    const weeks = days / 7;
    const months = days / 30;
    const years = days / 365;

    const isPast = diff > 0;
    const prefix = isPast ? '' : 'in ';
    const suffix = isPast ? ' ago' : '';

    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${prefix}${Math.floor(minutes)} minute${Math.floor(minutes) !== 1 ? 's' : ''}${suffix}`;
    if (hours < 24) return `${prefix}${Math.floor(hours)} hour${Math.floor(hours) !== 1 ? 's' : ''}${suffix}`;
    if (days < 7) return `${prefix}${Math.floor(days)} day${Math.floor(days) !== 1 ? 's' : ''}${suffix}`;
    if (weeks < 4) return `${prefix}${Math.floor(weeks)} week${Math.floor(weeks) !== 1 ? 's' : ''}${suffix}`;
    if (months < 12) return `${prefix}${Math.floor(months)} month${Math.floor(months) !== 1 ? 's' : ''}${suffix}`;
    return `${prefix}${Math.floor(years)} year${Math.floor(years) !== 1 ? 's' : ''}${suffix}`;
}

/**
 * Get current season based on Indian agricultural calendar
 * @param {Date} date - Date to check (defaults to now)
 * @returns {object} Season information
 */
function getCurrentSeason(date = new Date()) {
    const month = date.getMonth() + 1; // 1-12

    if (month >= 6 && month <= 10) {
        return {
            name: 'Kharif',
            hindi: 'खरीफ',
            description: 'Monsoon cropping season',
            crops: ['Rice', 'Maize', 'Cotton', 'Soybean', 'Groundnut'],
            startMonth: 'June',
            endMonth: 'October'
        };
    } else if (month >= 11 || month <= 3) {
        return {
            name: 'Rabi',
            hindi: 'रबी',
            description: 'Winter cropping season',
            crops: ['Wheat', 'Barley', 'Mustard', 'Chickpea', 'Potato'],
            startMonth: 'November',
            endMonth: 'March'
        };
    } else {
        return {
            name: 'Zaid',
            hindi: 'जायद',
            description: 'Summer cropping season',
            crops: ['Watermelon', 'Muskmelon', 'Cucumber', 'Moong'],
            startMonth: 'April',
            endMonth: 'June'
        };
    }
}

/**
 * Calculate days between two dates
 * @param {Date|string} startDate - Start date
 * @param {Date|string} endDate - End date
 * @returns {number} Number of days
 */
function daysBetween(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}


// ============================================================
// UNIT CONVERSION UTILITIES
// ============================================================

/**
 * Convert area between different units
 * @param {number} value - Value to convert
 * @param {string} fromUnit - Source unit
 * @param {string} toUnit - Target unit
 * @returns {number} Converted value
 */
function convertArea(value, fromUnit, toUnit) {
    const sqMetersConversion = {
        'hectare': 10000,
        'acre': 4046.86,
        'bigha': 2508.38,
        'square_meter': 1,
        'square_feet': 0.0929,
        'gunta': 101.17,
        'kanal': 505.857
    };

    const fromFactor = sqMetersConversion[fromUnit.toLowerCase()];
    const toFactor = sqMetersConversion[toUnit.toLowerCase()];

    if (!fromFactor || !toFactor) {
        throw new Error(`Unsupported unit. Use: ${Object.keys(sqMetersConversion).join(', ')}`);
    }

    const sqMeters = value * fromFactor;
    return parseFloat((sqMeters / toFactor).toFixed(4));
}

/**
 * Convert weight between different units
 * @param {number} value - Value to convert
 * @param {string} fromUnit - Source unit
 * @param {string} toUnit - Target unit
 * @returns {number} Converted value
 */
function convertWeight(value, fromUnit, toUnit) {
    const gramsConversion = {
        'kg': 1000,
        'quintal': 100000,
        'ton': 1000000,
        'gram': 1,
        'pound': 453.592,
        'maund': 37324.2
    };

    const fromFactor = gramsConversion[fromUnit.toLowerCase()];
    const toFactor = gramsConversion[toUnit.toLowerCase()];

    if (!fromFactor || !toFactor) {
        throw new Error(`Unsupported unit. Use: ${Object.keys(gramsConversion).join(', ')}`);
    }

    const grams = value * fromFactor;
    return parseFloat((grams / toFactor).toFixed(4));
}

/**
 * Convert temperature between Celsius and Fahrenheit
 * @param {number} value - Temperature value
 * @param {string} fromUnit - 'C' or 'F'
 * @returns {number} Converted temperature
 */
function convertTemperature(value, fromUnit) {
    if (fromUnit.toUpperCase() === 'C') {
        return parseFloat((value * 9/5 + 32).toFixed(2));
    } else if (fromUnit.toUpperCase() === 'F') {
        return parseFloat(((value - 32) * 5/9).toFixed(2));
    }
    throw new Error('Use "C" for Celsius or "F" for Fahrenheit');
}


// ============================================================
// CALCULATION UTILITIES
// ============================================================

/**
 * Calculate seed requirement
 * @param {string} crop - Crop name
 * @param {number} areaHectares - Area in hectares
 * @returns {object} Seed requirement details
 */
function calculateSeedRequirement(crop, areaHectares) {
    const seedRates = {
        'rice': { rate: 25, unit: 'kg/ha', method: 'transplanting' },
        'wheat': { rate: 100, unit: 'kg/ha', method: 'broadcasting' },
        'maize': { rate: 20, unit: 'kg/ha', method: 'drilling' },
        'cotton': { rate: 15, unit: 'kg/ha', method: 'drilling' },
        'soybean': { rate: 75, unit: 'kg/ha', method: 'drilling' },
        'groundnut': { rate: 100, unit: 'kg/ha', method: 'dibbling' },
        'tomato': { rate: 0.4, unit: 'kg/ha', method: 'transplanting' },
        'potato': { rate: 2500, unit: 'kg/ha', method: 'planting' },
        'onion': { rate: 8, unit: 'kg/ha', method: 'transplanting' }
    };

    const cropLower = crop.toLowerCase();
    if (!seedRates[cropLower]) {
        return { error: `Seed rate not available for ${crop}` };
    }

    const info = seedRates[cropLower];
    const quantity = info.rate * areaHectares;

    return {
        crop: crop,
        area: areaHectares,
        seedRate: `${info.rate} ${info.unit}`,
        totalQuantityKg: parseFloat(quantity.toFixed(2)),
        sowingMethod: info.method,
        additionalInfo: `Add 10-15% extra for gap filling`
    };
}

/**
 * Calculate fertilizer cost
 * @param {object} fertilizers - Object with fertilizer quantities
 * @returns {object} Cost breakdown
 */
function calculateFertilizerCost(fertilizers) {
    const prices = {
        'urea': 6,
        'dap': 27,
        'mop': 18,
        'ssp': 8,
        'npk': 25,
        'zinc_sulphate': 45,
        'boron': 150
    };

    let totalCost = 0;
    const breakdown = [];

    for (const [name, quantity] of Object.entries(fertilizers)) {
        const price = prices[name.toLowerCase()] || 20;
        const cost = quantity * price;
        totalCost += cost;
        breakdown.push({
            fertilizer: name,
            quantity: quantity,
            pricePerKg: price,
            cost: cost
        });
    }

    return {
        breakdown: breakdown,
        totalCost: parseFloat(totalCost.toFixed(2)),
        currency: 'INR'
    };
}

/**
 * Calculate expected profit
 * @param {string} crop - Crop name
 * @param {number} areaHectares - Area in hectares
 * @param {number} yieldPerHectare - Expected yield (kg/ha)
 * @param {number} pricePerKg - Market price per kg
 * @param {number} totalCost - Total input cost
 * @returns {object} Profit analysis
 */
function calculateExpectedProfit(crop, areaHectares, yieldPerHectare, pricePerKg, totalCost) {
    const totalYield = yieldPerHectare * areaHectares;
    const grossRevenue = totalYield * pricePerKg;
    const netProfit = grossRevenue - totalCost;
    const profitPerHectare = netProfit / areaHectares;
    const roi = ((netProfit / totalCost) * 100);

    return {
        crop: crop,
        area: areaHectares,
        yield: {
            perHectare: yieldPerHectare,
            total: totalYield,
            unit: 'kg'
        },
        revenue: {
            pricePerKg: pricePerKg,
            grossRevenue: parseFloat(grossRevenue.toFixed(2))
        },
        costs: {
            totalCost: totalCost
        },
        profit: {
            netProfit: parseFloat(netProfit.toFixed(2)),
            profitPerHectare: parseFloat(profitPerHectare.toFixed(2)),
            roi: parseFloat(roi.toFixed(2)) + '%'
        },
        currency: 'INR'
    };
}

/**
 * Calculate water requirement
 * @param {string} crop - Crop name
 * @param {number} areaHectares - Area in hectares
 * @param {string} irrigationType - 'flood', 'drip', 'sprinkler'
 * @returns {object} Water requirement details
 */
function calculateWaterRequirement(crop, areaHectares, irrigationType = 'flood') {
    const waterRequirements = {
        'rice': 1500,
        'wheat': 450,
        'maize': 600,
        'cotton': 900,
        'sugarcane': 2000,
        'tomato': 500,
        'potato': 550,
        'onion': 450
    };

    const efficiencyFactors = {
        'flood': 1.0,
        'drip': 0.5,
        'sprinkler': 0.7
    };

    const baseRequirement = waterRequirements[crop.toLowerCase()] || 600;
    const efficiency = efficiencyFactors[irrigationType.toLowerCase()] || 1.0;
    const adjustedRequirement = baseRequirement * efficiency;
    const totalWaterMM = adjustedRequirement * areaHectares;
    const totalWaterLiters = totalWaterMM * 10000; // mm to liters per hectare

    return {
        crop: crop,
        area: areaHectares,
        irrigationType: irrigationType,
        waterSavings: `${((1 - efficiency) * 100).toFixed(0)}%`,
        requirement: {
            perHectareMM: adjustedRequirement,
            totalMM: totalWaterMM,
            totalLiters: totalWaterLiters,
            totalCubicMeters: totalWaterLiters / 1000
        },
        irrigationSchedule: generateIrrigationSchedule(crop, irrigationType)
    };
}

/**
 * Generate irrigation schedule
 * @param {string} crop - Crop name
 * @param {string} irrigationType - Irrigation type
 * @returns {array} Schedule array
 */
function generateIrrigationSchedule(crop, irrigationType) {
    const intervals = {
        'flood': { hot: 5, normal: 7, cool: 10 },
        'drip': { hot: 1, normal: 2, cool: 3 },
        'sprinkler': { hot: 3, normal: 4, cool: 6 }
    };

    const interval = intervals[irrigationType] || intervals['flood'];
    
    return [
        { season: 'Summer (Hot)', interval: `Every ${interval.hot} days` },
        { season: 'Monsoon', interval: 'As needed based on rainfall' },
        { season: 'Winter (Cool)', interval: `Every ${interval.cool} days` }
    ];
}


// ============================================================
// VALIDATION UTILITIES
// ============================================================

/**
 * Validate phone number (Indian format)
 * @param {string} phone - Phone number
 * @returns {boolean} Is valid
 */
function validatePhoneNumber(phone) {
    const indianPhoneRegex = /^[+]?91[-\s]?[6-9]\d{9}$|^[6-9]\d{9}$/;
    return indianPhoneRegex.test(phone.replace(/\s/g, ''));
}

/**
 * Validate email address
 * @param {string} email - Email address
 * @returns {boolean} Is valid
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate Aadhaar number
 * @param {string} aadhaar - Aadhaar number
 * @returns {boolean} Is valid
 */
function validateAadhaar(aadhaar) {
    const aadhaarRegex = /^[2-9]{1}[0-9]{11}$/;
    return aadhaarRegex.test(aadhaar.replace(/\s/g, ''));
}

/**
 * Validate PIN code (Indian)
 * @param {string} pincode - PIN code
 * @returns {boolean} Is valid
 */
function validatePincode(pincode) {
    const pincodeRegex = /^[1-9][0-9]{5}$/;
    return pincodeRegex.test(pincode);
}

/**
 * Sanitize input string
 * @param {string} str - String to sanitize
 * @returns {string} Sanitized string
 */
function sanitizeInput(str) {
    if (typeof str !== 'string') return str;
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .trim();
}


// ============================================================
// UI HELPER UTILITIES
// ============================================================

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in ms
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${getToastIcon(type)}</span>
        <span class="toast-message">${sanitizeInput(message)}</span>
        <button class="toast-close">&times;</button>
    `;

    // Add styles if not exists
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .toast {
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10000;
                animation: slideIn 0.3s ease;
                max-width: 350px;
            }
            .toast-success { background: #10b981; color: white; }
            .toast-error { background: #ef4444; color: white; }
            .toast-warning { background: #f59e0b; color: white; }
            .toast-info { background: #3b82f6; color: white; }
            .toast-close { background: none; border: none; color: inherit; cursor: pointer; font-size: 18px; }
            @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
            @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(toast);

    // Close button handler
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    });

    // Auto remove
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

/**
 * Get toast icon based on type
 * @param {string} type - Toast type
 * @returns {string} Icon HTML
 */
function getToastIcon(type) {
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    return icons[type] || icons.info;
}

/**
 * Show loading spinner
 * @param {string} elementId - Element ID to show spinner in
 * @param {string} message - Loading message
 */
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>${sanitizeInput(message)}</p>
        </div>
    `;

    // Add styles if not exists
    if (!document.getElementById('loading-styles')) {
        const style = document.createElement('style');
        style.id = 'loading-styles';
        style.textContent = `
            .loading-spinner {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 40px;
            }
            .spinner {
                width: 40px;
                height: 40px;
                border: 4px solid #e5e7eb;
                border-top-color: #10b981;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Hide loading spinner
 * @param {string} elementId - Element ID
 */
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
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

/**
 * Throttle function
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in ms
 * @returns {Function} Throttled function
 */
function throttle(func, limit = 100) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Format number with Indian numbering system
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatIndianNumber(num) {
    const numStr = num.toString();
    const parts = numStr.split('.');
    let intPart = parts[0];
    const decPart = parts[1] ? '.' + parts[1] : '';

    // Indian numbering system
    let lastThree = intPart.slice(-3);
    let otherNumbers = intPart.slice(0, -3);
    if (otherNumbers !== '') {
        lastThree = ',' + lastThree;
    }
    const formatted = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + lastThree;
    
    return formatted + decPart;
}

/**
 * Format currency (INR)
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return '₹' + formatIndianNumber(parseFloat(amount.toFixed(2)));
}


// ============================================================
// LOCAL STORAGE UTILITIES
// ============================================================

/**
 * Save data to local storage
 * @param {string} key - Storage key
 * @param {any} data - Data to save
 */
function saveToStorage(key, data) {
    try {
        const serialized = JSON.stringify({
            data: data,
            timestamp: Date.now()
        });
        localStorage.setItem(key, serialized);
    } catch (error) {
        console.error('Error saving to storage:', error);
    }
}

/**
 * Get data from local storage
 * @param {string} key - Storage key
 * @param {number} maxAge - Maximum age in ms (optional)
 * @returns {any} Stored data or null
 */
function getFromStorage(key, maxAge = null) {
    try {
        const item = localStorage.getItem(key);
        if (!item) return null;

        const { data, timestamp } = JSON.parse(item);
        
        if (maxAge && Date.now() - timestamp > maxAge) {
            localStorage.removeItem(key);
            return null;
        }

        return data;
    } catch (error) {
        console.error('Error reading from storage:', error);
        return null;
    }
}

/**
 * Remove item from local storage
 * @param {string} key - Storage key
 */
function removeFromStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing from storage:', error);
    }
}

/**
 * Clear all AgriTech related storage
 */
function clearAgriStorage() {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
        if (key.startsWith('agri_') || key.startsWith('crop_') || key.startsWith('weather_')) {
            localStorage.removeItem(key);
        }
    });
}


// ============================================================
// EXPORT FOR MODULE USE
// ============================================================

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatDate,
        getRelativeTime,
        getCurrentSeason,
        daysBetween,
        convertArea,
        convertWeight,
        convertTemperature,
        calculateSeedRequirement,
        calculateFertilizerCost,
        calculateExpectedProfit,
        calculateWaterRequirement,
        validatePhoneNumber,
        validateEmail,
        validateAadhaar,
        validatePincode,
        sanitizeInput,
        showToast,
        showLoading,
        hideLoading,
        debounce,
        throttle,
        formatIndianNumber,
        formatCurrency,
        saveToStorage,
        getFromStorage,
        removeFromStorage,
        clearAgriStorage
    };
}

// Make available globally
window.AgriHelpers = {
    formatDate,
    getRelativeTime,
    getCurrentSeason,
    daysBetween,
    convertArea,
    convertWeight,
    convertTemperature,
    calculateSeedRequirement,
    calculateFertilizerCost,
    calculateExpectedProfit,
    calculateWaterRequirement,
    validatePhoneNumber,
    validateEmail,
    validateAadhaar,
    validatePincode,
    sanitizeInput,
    showToast,
    showLoading,
    hideLoading,
    debounce,
    throttle,
    formatIndianNumber,
    formatCurrency,
    saveToStorage,
    getFromStorage,
    removeFromStorage,
    clearAgriStorage
};
