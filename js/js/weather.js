/**
 * OPENWEATHERMAP API CONFIGURATION
 * To avoid security leaks, do not hardcode your API key here.
 * For development, you can temporarily paste your key, but ensure
 * it is removed before pushing to GitHub.
 */
const API_KEY = ''; 

/**
 * Fetches weather data and generates farming-specific advice
 * @param {string} city 
 */
async function fetchWeather(city = 'Mumbai') {
    // Safety check for API Key
    if (!API_KEY) {
        console.error("Weather Module: API Key is missing. Please add your OpenWeatherMap API key in js/weather.js");
        return null;
    }

    try {
        const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&units=metric&appid=${API_KEY}`);
        const data = await response.json();
        
        if (data.cod !== 200) throw new Error(data.message);
        
        return processWeatherData(data);
    } catch (error) {
        console.error("Weather Module Error:", error);
        return null;
    }
}

/**
 * Evaluates weather parameters based on specific farming thresholds
 * @param {object} data - Raw data from API
 */
function processWeatherData(data) {
    const temp = data.main.temp;
    const humidity = data.main.humidity;
    const windSpeed = data.wind.speed * 3.6; // Convert m/s to km/h
    const condition = data.weather[0].main;
    const cloudCover = data.clouds.all;

    let advice = [];
    let alertClass = "alert-info"; // Default blue

    // 1. Pesticide Alert: If wind speed > 15km/h, advise against spraying (prevents chemical drift).
    if (windSpeed > 15) {
        advice.push("🚫 <strong>Pesticide Alert:</strong> High wind speed detected (>15km/h). Avoid spraying to prevent chemical drift.");
        alertClass = "alert-warning";
    }

    // 2. Irrigation Alert: If humidity < 30% and Temp > 35°C, suggest increased watering.
    if (humidity < 30 && temp > 35) {
        advice.push("💧 <strong>Irrigation Alert:</strong> Extreme heat and low humidity. Suggest increased watering to protect crops.");
        alertClass = "alert-danger";
    }

    // 3. Sowing Alert: If rain probability (proxied by cloud cover or current rain) > 70%, suggest delaying sowing.
    if (data.rain || cloudCover > 70) {
        advice.push("🌱 <strong>Sowing Alert:</strong> High probability of rain. Delay sowing to prevent seed washout.");
        alertClass = "alert-warning";
    }

    // Default message if no alerts are triggered
    if (advice.length === 0) {
        advice.push("✅ <strong>Optimal Conditions:</strong> Weather conditions are suitable for general farming activities.");
        alertClass = "alert-success";
    }

    return {
        temp: Math.round(temp),
        humidity,
        windSpeed: windSpeed.toFixed(1),
        condition,
        advice: advice.join('<br>'),
        alertClass
    };
}