// Smart Irrigation Scheduler JavaScript
class IrrigationScheduler {
    constructor() {
        this.weatherAPIKey = 'YOUR_OPENWEATHER_API_KEY'; // Replace with actual API key
        this.cropWaterRequirements = this.initializeCropData();
        this.irrigationEfficiency = this.initializeIrrigationEfficiency();
        this.weatherData = null;
        this.currentSchedule = null;
        
        this.initializeEventListeners();
        this.loadStoredData();
    }

    // Initialize crop water requirement database
    initializeCropData() {
        return {
            wheat: {
                dailyWater: 4.5, // mm/day
                growthStages: {
                    seedling: { factor: 0.6, duration: 30 },
                    vegetative: { factor: 1.0, duration: 45 },
                    flowering: { factor: 1.2, duration: 20 },
                    grain: { factor: 0.8, duration: 25 }
                }
            },
            rice: {
                dailyWater: 6.0,
                growthStages: {
                    seedling: { factor: 0.7, duration: 25 },
                    vegetative: { factor: 1.1, duration: 50 },
                    flowering: { factor: 1.3, duration: 15 },
                    grain: { factor: 0.9, duration: 30 }
                }
            },
            corn: {
                dailyWater: 5.5,
                growthStages: {
                    seedling: { factor: 0.5, duration: 20 },
                    vegetative: { factor: 1.0, duration: 40 },
                    tasseling: { factor: 1.3, duration: 15 },
                    grain: { factor: 0.7, duration: 35 }
                }
            },
            cotton: {
                dailyWater: 4.0,
                growthStages: {
                    seedling: { factor: 0.6, duration: 25 },
                    vegetative: { factor: 1.0, duration: 50 },
                    flowering: { factor: 1.2, duration: 30 },
                    boll: { factor: 0.8, duration: 25 }
                }
            },
            sugarcane: {
                dailyWater: 7.0,
                growthStages: {
                    establishment: { factor: 0.8, duration: 60 },
                    vegetative: { factor: 1.1, duration: 120 },
                    maturity: { factor: 0.9, duration: 60 }
                }
            },
            pulses: {
                dailyWater: 3.5,
                growthStages: {
                    seedling: { factor: 0.7, duration: 20 },
                    vegetative: { factor: 1.0, duration: 30 },
                    flowering: { factor: 1.1, duration: 15 },
                    pod: { factor: 0.8, duration: 20 }
                }
            },
            vegetables: {
                dailyWater: 4.0,
                growthStages: {
                    seedling: { factor: 0.6, duration: 15 },
                    vegetative: { factor: 1.0, duration: 25 },
                    fruiting: { factor: 1.2, duration: 20 }
                }
            },
            fruits: {
                dailyWater: 5.0,
                growthStages: {
                    dormancy: { factor: 0.3, duration: 90 },
                    flowering: { factor: 1.1, duration: 20 },
                    fruiting: { factor: 1.2, duration: 60 },
                    harvest: { factor: 0.8, duration: 30 }
                }
            }
        };
    }

    // Initialize irrigation method efficiency
    initializeIrrigationEfficiency() {
        return {
            drip: 0.95,
            sprinkler: 0.75,
            flood: 0.60,
            manual: 0.70
        };
    }

    // Initialize event listeners
    initializeEventListeners() {
        // Soil moisture slider
        const moistureSlider = document.getElementById('soil-moisture');
        const moistureValue = document.querySelector('.moisture-value');
        
        moistureSlider.addEventListener('input', (e) => {
            moistureValue.textContent = `${e.target.value}%`;
        });

        // Form submission
        const form = document.getElementById('irrigation-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateSchedule();
        });
    }

    // Load stored data from localStorage
    loadStoredData() {
        const storedUsage = localStorage.getItem('waterUsage');
        if (storedUsage) {
            const usage = JSON.parse(storedUsage);
            this.updateWaterTracker(usage);
        }
    }

    // Generate irrigation schedule
    async generateSchedule() {
        const formData = this.getFormData();
        if (!this.validateFormData(formData)) {
            return;
        }

        this.showLoadingModal();

        try {
            // Get weather data
            await this.fetchWeatherData(formData.location);
            
            // Generate schedule
            this.currentSchedule = this.calculateIrrigationSchedule(formData);
            
            // Update UI
            this.displayResults(formData);
            this.hideLoadingModal();
            
            // Store data
            this.storeScheduleData(formData);
            
        } catch (error) {
            console.error('Error generating schedule:', error);
            this.hideLoadingModal();
            this.showError('Failed to generate schedule. Please try again.');
        }
    }

    // Get form data
    getFormData() {
        return {
            cropType: document.getElementById('crop-type').value,
            farmSize: parseFloat(document.getElementById('farm-size').value),
            irrigationMethod: document.getElementById('irrigation-method').value,
            soilType: document.getElementById('soil-type').value,
            soilMoisture: parseInt(document.getElementById('soil-moisture').value),
            location: document.getElementById('location').value
        };
    }

    // Validate form data
    validateFormData(data) {
        if (!data.cropType || !data.farmSize || !data.irrigationMethod || !data.location) {
            this.showError('Please fill in all required fields.');
            return false;
        }
        if (data.farmSize <= 0) {
            this.showError('Farm size must be greater than 0.');
            return false;
        }
        return true;
    }

    // Fetch weather data from OpenWeatherMap API
    async fetchWeatherData(location) {
        try {
            // For demo purposes, using mock weather data
            // In production, replace with actual API call:
            // const response = await fetch(`https://api.openweathermap.org/data/2.5/forecast?q=${location}&appid=${this.weatherAPIKey}&units=metric`);
            // this.weatherData = await response.json();
            
            this.weatherData = this.generateMockWeatherData();
        } catch (error) {
            console.error('Error fetching weather data:', error);
            // Use mock data as fallback
            this.weatherData = this.generateMockWeatherData();
        }
    }

    // Generate mock weather data for demonstration
    generateMockWeatherData() {
        const today = new Date();
        const weatherData = {
            location: 'Demo City',
            forecast: []
        };

        for (let i = 0; i < 7; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            
            weatherData.forecast.push({
                date: date,
                temperature: 25 + Math.random() * 10,
                humidity: 60 + Math.random() * 20,
                rainfall: Math.random() > 0.7 ? Math.random() * 10 : 0,
                windSpeed: Math.random() * 15
            });
        }

        return weatherData;
    }

    // Calculate irrigation schedule
    calculateIrrigationSchedule(farmData) {
        const crop = this.cropWaterRequirements[farmData.cropType];
        const efficiency = this.irrigationEfficiency[farmData.irrigationMethod];
        const schedule = [];

        // Calculate base water requirement
        const baseWaterRequirement = crop.dailyWater * farmData.farmSize * 2.47; // Convert to gallons
        const adjustedRequirement = baseWaterRequirement / efficiency;

        // Generate 7-day schedule
        for (let i = 0; i < 7; i++) {
            const dayWeather = this.weatherData.forecast[i];
            const daySchedule = this.calculateDaySchedule(
                farmData, 
                dayWeather, 
                adjustedRequirement,
                i
            );
            schedule.push(daySchedule);
        }

        return schedule;
    }

    // Calculate schedule for a specific day
    calculateDaySchedule(farmData, weather, baseRequirement, dayIndex) {
        const date = new Date();
        date.setDate(date.getDate() + dayIndex);
        
        let waterRequired = baseRequirement;
        let shouldIrrigate = true;
        let reason = '';

        // Adjust based on weather conditions
        if (weather.rainfall > 5) {
            shouldIrrigate = false;
            reason = 'Rain expected - skip irrigation';
            waterRequired = 0;
        } else if (weather.temperature > 35) {
            waterRequired *= 1.3; // Increase by 30% for high temperature
            reason = 'High temperature - increase watering';
        } else if (weather.temperature < 15) {
            waterRequired *= 0.7; // Decrease by 30% for low temperature
            reason = 'Low temperature - reduce watering';
        }

        // Adjust based on soil moisture
        if (farmData.soilMoisture > 80) {
            shouldIrrigate = false;
            reason = 'Soil moisture sufficient';
            waterRequired = 0;
        } else if (farmData.soilMoisture < 30) {
            waterRequired *= 1.2; // Increase by 20% for dry soil
            reason = 'Low soil moisture - increase watering';
        }

        // Adjust based on soil type
        if (farmData.soilType === 'clay') {
            waterRequired *= 0.8; // Clay retains water better
        } else if (farmData.soilType === 'sandy') {
            waterRequired *= 1.2; // Sandy soil needs more water
        }

        return {
            date: date,
            shouldIrrigate: shouldIrrigate,
            waterRequired: Math.round(waterRequired * 100) / 100,
            duration: this.calculateIrrigationDuration(waterRequired, farmData.irrigationMethod),
            reason: reason,
            weather: weather
        };
    }

    // Calculate irrigation duration
    calculateIrrigationDuration(waterRequired, method) {
        const flowRates = {
            drip: 0.5,      // 0.5 gallons per minute per emitter
            sprinkler: 2.0,  // 2.0 gallons per minute
            flood: 10.0,     // 10.0 gallons per minute
            manual: 1.0      // 1.0 gallons per minute
        };

        const flowRate = flowRates[method];
        const duration = waterRequired / flowRate;
        
        return Math.round(duration * 10) / 10; // Round to 1 decimal place
    }

    // Display results
    displayResults(farmData) {
        const resultsSection = document.getElementById('results-section');
        resultsSection.style.display = 'block';

        // Update weather alert
        this.updateWeatherAlert();

        // Update summary cards
        this.updateSummaryCards();

        // Update weekly schedule
        this.updateWeeklySchedule();

        // Update water tracker
        this.updateWaterTrackerFromSchedule();

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Update weather alert
    updateWeatherAlert() {
        const alertMessage = document.getElementById('alert-message');
        const weatherAlert = document.getElementById('weather-alert');
        
        const todayWeather = this.weatherData.forecast[0];
        let message = '';
        let alertClass = '';

        if (todayWeather.rainfall > 5) {
            message = `Rain expected today (${todayWeather.rainfall.toFixed(1)}mm) - Skip irrigation to save water!`;
            alertClass = 'rain-alert';
        } else if (todayWeather.temperature > 35) {
            message = `Heatwave alert! Temperature: ${todayWeather.temperature.toFixed(1)}°C - Increase watering frequency.`;
            alertClass = 'heat-alert';
        } else if (todayWeather.temperature < 15) {
            message = `Cold weather alert! Temperature: ${todayWeather.temperature.toFixed(1)}°C - Reduce watering.`;
            alertClass = 'cold-alert';
        } else {
            message = `Good weather conditions for irrigation. Temperature: ${todayWeather.temperature.toFixed(1)}°C, Humidity: ${todayWeather.humidity.toFixed(1)}%`;
            alertClass = 'good-alert';
        }

        alertMessage.textContent = message;
        weatherAlert.className = `weather-alert ${alertClass}`;
    }

    // Update summary cards
    updateSummaryCards() {
        const nextIrrigation = this.currentSchedule.find(day => day.shouldIrrigate);
        
        document.getElementById('next-irrigation').textContent = 
            nextIrrigation ? nextIrrigation.date.toLocaleDateString() : 'No irrigation needed';
        
        const totalWater = this.currentSchedule.reduce((sum, day) => sum + day.waterRequired, 0);
        document.getElementById('water-required').textContent = `${totalWater.toFixed(1)} gallons`;
        
        const totalDuration = this.currentSchedule.reduce((sum, day) => sum + day.duration, 0);
        document.getElementById('irrigation-duration').textContent = `${totalDuration.toFixed(1)} minutes`;
    }

    // Update weekly schedule
    updateWeeklySchedule() {
        const scheduleGrid = document.getElementById('schedule-grid');
        scheduleGrid.innerHTML = '';

        this.currentSchedule.forEach(day => {
            const dayElement = document.createElement('div');
            dayElement.className = `schedule-day ${day.shouldIrrigate ? 'irrigation-day' : 'no-irrigation'}`;
            
            const dayName = day.date.toLocaleDateString('en-US', { weekday: 'short' });
            const date = day.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            
            dayElement.innerHTML = `
                <h4>${dayName}</h4>
                <p>${date}</p>
                <div class="status">${day.shouldIrrigate ? 'Irrigate' : 'Skip'}</div>
                ${day.shouldIrrigate ? `<small>${day.waterRequired.toFixed(1)} gal</small>` : ''}
            `;
            
            scheduleGrid.appendChild(dayElement);
        });
    }

    // Update water tracker from schedule
    updateWaterTrackerFromSchedule() {
        const weeklyUsage = this.currentSchedule.reduce((sum, day) => sum + day.waterRequired, 0);
        const monthlyUsage = weeklyUsage * 4; // Approximate monthly usage
        const waterSaved = weeklyUsage * 0.2; // Assume 20% water saving with smart scheduling

        const usageData = {
            weekly: weeklyUsage,
            monthly: monthlyUsage,
            saved: waterSaved
        };

        this.updateWaterTracker(usageData);
        localStorage.setItem('waterUsage', JSON.stringify(usageData));
    }

    // Update water tracker display
    updateWaterTracker(usageData) {
        document.getElementById('weekly-usage').textContent = `${usageData.weekly.toFixed(1)} gal`;
        document.getElementById('monthly-usage').textContent = `${usageData.monthly.toFixed(1)} gal`;
        document.getElementById('water-saved').textContent = `${usageData.saved.toFixed(1)} gal`;
    }

    // Store schedule data
    storeScheduleData(farmData) {
        const scheduleData = {
            farmData: farmData,
            schedule: this.currentSchedule,
            generatedAt: new Date().toISOString()
        };
        localStorage.setItem('irrigationSchedule', JSON.stringify(scheduleData));
    }

    // Show loading modal
    showLoadingModal() {
        document.getElementById('loading-modal').style.display = 'flex';
    }

    // Hide loading modal
    hideLoadingModal() {
        document.getElementById('loading-modal').style.display = 'none';
    }

    // Show error message
    showError(message) {
        alert(message); // In production, use a proper toast notification
    }
}

// Initialize the scheduler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new IrrigationScheduler();
});

// Add some interactive features
document.addEventListener('DOMContentLoaded', () => {
    // Add hover effects to schedule days
    document.addEventListener('mouseover', (e) => {
        if (e.target.closest('.schedule-day')) {
            e.target.closest('.schedule-day').style.transform = 'scale(1.05)';
        }
    });

    document.addEventListener('mouseout', (e) => {
        if (e.target.closest('.schedule-day')) {
            e.target.closest('.schedule-day').style.transform = 'scale(1)';
        }
    });

    // Add click to expand schedule details
    document.addEventListener('click', (e) => {
        if (e.target.closest('.schedule-day')) {
            const dayElement = e.target.closest('.schedule-day');
            const dayIndex = Array.from(dayElement.parentNode.children).indexOf(dayElement);
            
            if (window.irrigationScheduler && window.irrigationScheduler.currentSchedule) {
                const dayData = window.irrigationScheduler.currentSchedule[dayIndex];
                if (dayData) {
                    alert(`Schedule for ${dayData.date.toLocaleDateString()}:\n` +
                          `Irrigation: ${dayData.shouldIrrigate ? 'Yes' : 'No'}\n` +
                          `Water Required: ${dayData.waterRequired} gallons\n` +
                          `Duration: ${dayData.duration} minutes\n` +
                          `Reason: ${dayData.reason}`);
                }
            }
        }
    });
});
