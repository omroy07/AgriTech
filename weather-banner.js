// weather-banner.js - Weather Advisory Banner Logic

class WeatherAdvisoryBanner {
  constructor(options = {}) {
    this.apiKey = options.apiKey || "005186776a4c4589a6e90608250407"; // Your existing weather API key
    this.defaultLocation = options.location || "New Delhi";
    this.updateInterval = options.updateInterval || 1800000; // 30 minutes
    this.bannerId = options.bannerId || "weather-advisory-banner";
    this.autoHide = options.autoHide !== false;
    
    this.init();
  }

  async init() {
    await this.fetchWeatherAndDisplay();
    
    // Auto-update every 30 minutes
    setInterval(() => {
      this.fetchWeatherAndDisplay();
    }, this.updateInterval);
  }

  async fetchWeatherAndDisplay() {
    const banner = document.getElementById(this.bannerId);
    if (!banner) {
      console.warn(`Weather banner element #${this.bannerId} not found`);
      return;
    }

    try {
      banner.classList.add('loading');
      
      const weather = await this.fetchWeather(this.defaultLocation);
      this.renderBanner(banner, weather);
      
      banner.classList.remove('loading');
    } catch (error) {
      console.error('Weather banner error:', error);
      banner.classList.remove('loading');
      this.renderError(banner);
    }
  }

  async fetchWeather(location) {
    const url = `https://api.weatherapi.com/v1/current.json?key=${this.apiKey}&q=${location}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch weather data');
    }
    
    return await response.json();
  }

  generateAdvisory(weatherData) {
    const temp = weatherData.current.temp_c;
    const condition = weatherData.current.condition.text.toLowerCase();
    const windSpeed = weatherData.current.wind_kph;
    const humidity = weatherData.current.humidity;
    const isDay = weatherData.current.is_day;

    let advisory = { message: '', severity: 'info', icon: 'fa-cloud-sun' };

    // Rain advisory
    if (condition.includes('rain') || condition.includes('drizzle') || condition.includes('shower')) {
      advisory = {
        message: '🌧️ Rain detected. Avoid spraying pesticides/fertilizers today. Good for irrigation-free days.',
        severity: 'warning',
        icon: 'fa-cloud-rain'
      };
    }
    // High wind advisory
    else if (windSpeed > 20) {
      advisory = {
        message: '💨 High winds detected. Avoid drone operations and spraying. Secure lightweight equipment.',
        severity: 'warning',
        icon: 'fa-wind'
      };
    }
    // Frost warning
    else if (temp < 5 && !isDay) {
      advisory = {
        message: '❄️ Frost risk tonight. Cover sensitive crops. Check irrigation systems for freezing.',
        severity: 'danger',
        icon: 'fa-snowflake'
      };
    }
    // Extreme heat
    else if (temp > 35) {
      advisory = {
        message: '🔥 High temperature alert. Increase irrigation frequency. Avoid midday field work.',
        severity: 'danger',
        icon: 'fa-temperature-high'
      };
    }
    // Low humidity (drought risk)
    else if (humidity < 30 && temp > 28) {
      advisory = {
        message: '🏜️ Low humidity detected. Monitor soil moisture closely. Consider drip irrigation.',
        severity: 'warning',
        icon: 'fa-droplet-slash'
      };
    }
    // High humidity (disease risk)
    else if (humidity > 80 && temp > 20) {
      advisory = {
        message: '💧 High humidity - increased fungal disease risk. Monitor crops for signs of infection.',
        severity: 'info',
        icon: 'fa-droplet'
      };
    }
    // Thunderstorm
    else if (condition.includes('thunder') || condition.includes('storm')) {
      advisory = {
        message: '⚡ Thunderstorm warning. Stay indoors. Unplug sensitive electronics. Avoid field operations.',
        severity: 'danger',
        icon: 'fa-bolt'
      };
    }
    // Perfect conditions
    else if (temp >= 15 && temp <= 28 && humidity >= 40 && humidity <= 70) {
      advisory = {
        message: '✅ Excellent farming conditions today. Good for spraying, planting, and field operations.',
        severity: 'success',
        icon: 'fa-check-circle'
      };
    }
    // Default
    else {
      advisory = {
        message: `☁️ ${condition.charAt(0).toUpperCase() + condition.slice(1)}. Monitor crop conditions regularly.`,
        severity: 'info',
        icon: 'fa-cloud-sun'
      };
    }

    return advisory;
  }

  renderBanner(banner, weatherData) {
    const advisory = this.generateAdvisory(weatherData);
    const { location, current } = weatherData;

    // Set severity class
    banner.className = `weather-advisory-banner severity-${advisory.severity}`;

    banner.innerHTML = `
      <div class="weather-banner-left">
        <div class="weather-icon">
          <i class="fas ${advisory.icon}"></i>
        </div>
        <div class="weather-info">
          <div class="weather-location">${location.name}, ${location.region}</div>
          <div class="weather-temp">${Math.round(current.temp_c)}°C</div>
          <div class="weather-condition">${current.condition.text}</div>
        </div>
      </div>

      <div class="weather-banner-center">
        <div class="advisory-message">
          <span>${advisory.message}</span>
        </div>
      </div>

      <div class="weather-banner-right">
        <div class="weather-stat">
          <i class="fas fa-droplet"></i>
          <span>${current.humidity}%</span>
        </div>
        <div class="weather-stat">
          <i class="fas fa-wind"></i>
          <span>${Math.round(current.wind_kph)} km/h</span>
        </div>
      </div>

      ${this.autoHide ? '<button class="banner-close" aria-label="Close weather banner"><i class="fas fa-times"></i></button>' : ''}
    `;

    // Add close button handler
    if (this.autoHide) {
      const closeBtn = banner.querySelector('.banner-close');
      closeBtn.addEventListener('click', () => {
        banner.classList.add('hidden');
        // Remember user dismissed it (24 hours)
        sessionStorage.setItem('weather_banner_dismissed', Date.now());
      });
    }
  }

  renderError(banner) {
    banner.className = 'weather-advisory-banner severity-info';
    banner.innerHTML = `
      <div class="weather-banner-left">
        <div class="weather-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <div class="weather-info">
          <div class="weather-temp">Weather Unavailable</div>
          <div class="weather-condition">Check your connection</div>
        </div>
      </div>
      <div class="weather-banner-center">
        <div class="advisory-message">
          <span>Unable to fetch weather data. Please try again later.</span>
        </div>
      </div>
    `;
  }

  // Public method to update location
  updateLocation(newLocation) {
    this.defaultLocation = newLocation;
    this.fetchWeatherAndDisplay();
  }

  // Public method to show banner again
  show() {
    const banner = document.getElementById(this.bannerId);
    if (banner) {
      banner.classList.remove('hidden');
      sessionStorage.removeItem('weather_banner_dismissed');
    }
  }
}

// Auto-initialize if banner element exists
document.addEventListener('DOMContentLoaded', () => {
  const bannerElement = document.getElementById('weather-advisory-banner');
  
  if (bannerElement) {
    // Check if user dismissed it recently
    const dismissed = sessionStorage.getItem('weather_banner_dismissed');
    const isDismissedRecently = dismissed && (Date.now() - parseInt(dismissed) < 86400000); // 24 hours
    
    if (!isDismissedRecently) {
      // Initialize banner
      window.weatherBanner = new WeatherAdvisoryBanner({
        location: 'Punjab, India', // Change this based on user's location
        updateInterval: 1800000, // Update every 30 minutes
        autoHide: true
      });
    } else {
      bannerElement.classList.add('hidden');
    }
  }
});