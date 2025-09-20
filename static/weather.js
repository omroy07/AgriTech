//So to get current weather for London: 
// JSON: http://api.weatherapi.com/v1/current.json?key=<YOUR_API_KEY>&q=London

//To get 7 day weather for US Zipcode 07112: 
// JSON: http://api.weatherapi.com/v1/forecast.json?key=<YOUR_API_KEY>&q=07112&days=7


key = "005186776a4c4589a6e90608250407";
url ="https://api.weatherapi.com/v1";

const locationInput = document.getElementById('cityInput');
const searchButton = document.getElementById('search');   
const getCity = document.getElementById('city');
const getRegion = document.getElementById('region');
const getCountry = document.getElementById('country');
const getTemperature = document.getElementById('temperature');
const getDescription = document.getElementById('description');

//default city
window.onload = () => {
    fetchWeather("New Delhi");
}

//dynamic background
function updateBackground(conditionText) {
    const body = document.body;
    let imageUrl = '';

    const lowerCaseCondition = conditionText.toLowerCase();

    if (lowerCaseCondition.includes('sunny') || lowerCaseCondition.includes('clear') || lowerCaseCondition.includes('sun')) {
        imageUrl = 'https://wallpapers.com/images/hd/sunny-day-wallpaper-f21ok5dhnkco3i5n.jpg';
    } else if (lowerCaseCondition.includes('cloudy') || lowerCaseCondition.includes('overcast') || lowerCaseCondition.includes('mist') || lowerCaseCondition.includes('cloud')) {
        imageUrl = 'https://pics.freeartbackgrounds.com/midle/Cloudy_Sky_Background-1520.jpg';
    } else if (lowerCaseCondition.includes('rain') || lowerCaseCondition.includes('drizzle') || lowerCaseCondition.includes('shower') || lowerCaseCondition.includes('rainy')) {
        imageUrl = 'https://static.vecteezy.com/system/resources/previews/046/982/857/non_2x/monsoon-season-rainy-season-illustration-of-heavy-rain-illustration-of-rain-cloud-vector.jpg';
    } else if (lowerCaseCondition.includes('snow') || lowerCaseCondition.includes('sleet') || lowerCaseCondition.includes('ice') || lowerCaseCondition.includes('snowy')) {
        imageUrl = 'https://images.unsplash.com/photo-1542382441-2a6237890635?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';
    } else if (lowerCaseCondition.includes('thunder') || lowerCaseCondition.includes('storm') || lowerCaseCondition.includes('thundery') || lowerCaseCondition.includes('stormy')) {
        imageUrl = 'https://images.unsplash.com/photo-1507663249114-1e523a502626?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';
    }else if (lowerCaseCondition.includes('fog') || lowerCaseCondition.includes('foggy') || lowerCaseCondition.includes('dew') || lowerCaseCondition.includes('dewy')) {
        imageUrl = 'https://unsplash.com/photos/a-foggy-view-of-the-golden-gate-bridge-6tiPnI_ijuI';
    } else {
        imageUrl = 'https://www.transparenttextures.com/patterns/clean-textile.png';
    }

    body.style.backgroundImage = `url('${imageUrl}')`;
    body.style.backgroundSize = 'cover';
    body.style.backgroundPosition = 'center';
    body.style.backgroundRepeat = 'no-repeat';
    body.style.backgroundAttachment = 'fixed';
}

searchButton.addEventListener('click',() => {
    const location = locationInput.value;
    if (location){
        fetchWeather(location);
    }
});
locationInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        searchButton.click();
    }
});

async function fetchWeather(location){

    //------------------for Current Weather-------------------------------
    const currentWeatherURL= `${url}/current.json?key=${key}&q=${location}`;

    try {
        const response = await fetch(currentWeatherURL);
        if (response.ok) {
            const data = await response.json();
            displayWeather(data);
            updateBackground(data.current.condition.text);
        }
    } catch (error) {
        console.log("Error fetching data", error);
    }


    //------------------for hourly data----------------------------------
    const hourNow = new Date().getHours();
    const hourDisplay = 24 - hourNow;
    if(hourDisplay == 0){
        hourDisplay = 24;
    }

    let i=1;
    while(i<(hourDisplay+1)){
        const forecastHourlyURL= `${url}/forecast.json?key=${key}&q=${location}&hour=${hourNow}+${i}`;
        try {
            const response = await fetch(forecastHourlyURL);
            if (response.ok) {
                const data = await response.json();
                displayHourlyForecast(data); 
            }
        } catch (error) {
            console.log("Error fetching data", error);
        }
        i++;
    }

    //-----------------------for 10 days data----------------------------
    const forecastURL= `${url}/forecast.json?key=${key}&q=${location}&days=10`;

    try {
        const response = await fetch(forecastURL);
        if (response.ok) {
            const data = await response.json();
            displayDaywiseForecast(data); 
        }
    } catch (error) {
        console.log("Error fetching data", error);
    }
}

//general data
function displayWeather(data){

    // for Current Weather
    getCity.textContent= data.location.name;
    getRegion.textContent= data.location.region;
    getCountry.textContent= data.location.country;
    getTemperature.textContent = `${data.current.temp_c}°C`;
    getDescription.textContent = data.current.condition.text;

    var imageAdd = document.createElement("img");
    imageAdd.src = `https:${data.current.condition.icon}`;
    imageAdd.alt = data.current.condition.text;
    getTemperature.appendChild(imageAdd);
}

//hourly weather data
function displayHourlyForecast(data){

    const hourlyForecastContainer = document.getElementById('hour');
    hourlyForecastContainer.innerHTML = ''; 
    const todayHourlyForecast = data.forecast.forecastday[0].hour; //today's hourly data

    const currentHour = new Date(data.location.localtime).getHours();

    todayHourlyForecast.forEach(hourData => {
        const hour = new Date(hourData.time).getHours();
    
        if (hour > currentHour) {
            const hourlyCard = document.createElement('div');
            hourlyCard.classList.add('hData-card');
            hourlyCard.innerHTML = `
                <p class="time">${hour}</p>
                <img src="https:${hourData.condition.icon}" alt="${hourData.condition.text}" />
                <p class="temp">${hourData.temp_c}°C</p>
            `;
            hourlyForecastContainer.appendChild(hourlyCard);
        }
    });
}

//daywise weather
function displayDaywiseForecast(data){

    const dayWiseForecastContainer = document.getElementById('day');
    dayWiseForecastContainer.innerHTML = ''; 
    const forecastCollection = data.forecast.forecastday;
   
    forecastCollection.forEach(forecastData => {
        const forecastCard = document.createElement('div');
        forecastCard.classList.add('dayData-card');
        forecastCard.innerHTML = `
            <p class="date">${forecastData.date}</p>
            <img src="https:${forecastData.day.condition.icon}" alt="${forecastData.day.condition.text}" />
            <p class="temp">${forecastData.day.maxtemp_c}°C / ${forecastData.day.mintemp_c}°C </p>
        `;
        dayWiseForecastContainer.appendChild(forecastCard);
    });
}