// Main JavaScript for AQI Forecast App

document.addEventListener('DOMContentLoaded', function() {
    // Check model status on page load
    fetchModelStatus();
    
    // Form submission handler
    document.getElementById('prediction-form').addEventListener('submit', function(e) {
        e.preventDefault();
        getPrediction();
    });
});

// Fetch model status
function fetchModelStatus() {
    fetch('/model_status')
        .then(response => response.json())
        .then(data => {
            const statusContainer = document.getElementById('model-status');
            
            if (data.error) {
                statusContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i> Error checking model status: ${data.error}
                    </div>
                `;
                return;
            }
            
            let html = '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Model</th><th>Status</th><th>Last Updated</th></tr></thead>';
            html += '<tbody>';
            
            // Random Forest model status
            html += `
                <tr>
                    <td>Random Forest</td>
                    <td>
                        <span class="model-status-badge ${data.rf_model.available ? 'status-online' : 'status-offline'}">
                            ${data.rf_model.available ? 'Available' : 'Unavailable'}
                        </span>
                    </td>
                    <td>${data.rf_model.last_updated}</td>
                </tr>
            `;
            
            // SGD model status
            html += `
                <tr>
                    <td>SGD (Realtime)</td>
                    <td>
                        <span class="model-status-badge ${data.sgd_model.available ? 'status-online' : 'status-offline'}">
                            ${data.sgd_model.available ? 'Available' : 'Unavailable'}
                        </span>
                    </td>
                    <td>${data.sgd_model.last_updated}</td>
                </tr>
            `;
            
            html += '</tbody></table></div>';
            statusContainer.innerHTML = html;
        })
        .catch(error => {
            document.getElementById('model-status').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> Failed to connect to server
                </div>
            `;
            console.error('Error fetching model status:', error);
        });
}

// Get AQI prediction
function getPrediction() {
    // Show loading indicators
    document.getElementById('prediction-result').innerHTML = `
        <div class="d-flex justify-content-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    document.getElementById('forecast-result').innerHTML = `
        <div class="d-flex justify-content-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Get form values
    const temperature = document.getElementById('temperature').value;
    const humidity = document.getElementById('humidity').value;
    const windSpeed = document.getElementById('wind_speed').value;
    const pressure = document.getElementById('pressure').value;
    const modelType = document.querySelector('input[name="model_type"]:checked').value;
    
    // Create request body
    const requestBody = {
        temperature: temperature,
        humidity: humidity,
        wind_speed: windSpeed,
        pressure: pressure,
        model_type: modelType
    };
    
    // Send request to API
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
            return;
        }
        
        // Display current AQI prediction
        displayCurrentAQI(data);
        
        // Display forecast
        displayForecast(data.forecast);
    })
    .catch(error => {
        showError('Failed to connect to server');
        console.error('Error getting prediction:', error);
    });
}

// Display current AQI prediction
function displayCurrentAQI(data) {
    const container = document.getElementById('prediction-result');
    const category = data.category;
    const aqi = Math.round(data.current_aqi);
    
    let html = `
        <div class="mb-2">
            <span class="aqi-category aqi-${getCategoryClass(category.level)}">${category.level}</span>
        </div>
        <div class="aqi-display">${aqi}</div>
        <p class="mb-1">${category.message}</p>
        <p class="mt-3 text-muted small">
            <i class="fas fa-info-circle"></i> 
            Prediction made using ${data.model_used === 'rf' ? 'Random Forest' : 'SGD'} model
        </p>
    `;
    
    container.innerHTML = html;
    
    // Change the card header color based on AQI category
    const cardHeader = container.closest('.card').querySelector('.card-header');
    cardHeader.className = `card-header text-white bg-${getBootstrapColor(category.level)}`;
}

// Display forecast data
function displayForecast(forecast) {
    const container = document.getElementById('forecast-result');
    
    if (!forecast || forecast.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i> No forecast data available
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Create forecast display
    forecast.forEach(day => {
        const date = new Date(day.date).toLocaleDateString('en-US', { 
            weekday: 'short', 
            month: 'short', 
            day: 'numeric' 
        });
        
        const aqi = Math.round(day.aqi);
        const category = getAQICategory(aqi);
        
        html += `
            <div class="forecast-item" style="background-color: ${getCategoryColorBg(category)}">
                <div>
                    <strong>${date}</strong>
                </div>
                <div>
                    <span class="badge bg-${getBootstrapColor(category)}">${category}</span>
                    <strong>${aqi}</strong>
                </div>
            </div>
        `;
    });
    
    // Add chart canvas
    html += '<canvas id="forecast-chart" height="200"></canvas>';
    
    container.innerHTML = html;
    
    // Create chart
    createForecastChart(forecast);
}

// Create forecast chart using Chart.js
function createForecastChart(forecast) {
    const ctx = document.getElementById('forecast-chart').getContext('2d');
    
    const dates = forecast.map(day => {
        const date = new Date(day.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const aqiValues = forecast.map(day => day.aqi);
    
    const colors = aqiValues.map(aqi => getCategoryColor(getAQICategory(aqi)));
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'AQI Forecast',
                data: aqiValues,
                backgroundColor: colors,
                borderColor: colors.map(color => darkenColor(color, 20)),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'AQI Value'
                    }
                }
            }
        }
    });
}

// Show error message
function showError(message) {
    document.getElementById('prediction-result').innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> ${message}
        </div>
    `;
    
    document.getElementById('forecast-result').innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> Forecast unavailable
        </div>
    `;
}

// Helper functions for AQI category styling
function getAQICategory(aqi) {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for Sensitive Groups';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very Unhealthy';
    return 'Hazardous';
}

function getCategoryClass(category) {
    category = category.toLowerCase();
    if (category.includes('good')) return 'good';
    if (category.includes('moderate')) return 'moderate';
    if (category.includes('sensitive')) return 'unhealthy-sensitive';
    if (category.includes('unhealthy') && !category.includes('very')) return 'unhealthy';
    if (category.includes('very')) return 'very-unhealthy';
    return 'hazardous';
}

function getBootstrapColor(category) {
    category = typeof category === 'string' ? category.toLowerCase() : '';
    if (category.includes('good')) return 'success';
    if (category.includes('moderate')) return 'warning';
    if (category.includes('sensitive')) return 'warning';
    if (category.includes('unhealthy') && !category.includes('very')) return 'danger';
    if (category.includes('very')) return 'dark';
    return 'dark';
}

function getCategoryColor(category) {
    category = typeof category === 'string' ? category.toLowerCase() : '';
    if (category.includes('good')) return '#00e400';
    if (category.includes('moderate')) return '#ffff00';
    if (category.includes('sensitive')) return '#ff7e00';
    if (category.includes('unhealthy') && !category.includes('very')) return '#ff0000';
    if (category.includes('very')) return '#8f3f97';
    return '#7e0023';
}

function getCategoryColorBg(category) {
    category = typeof category === 'string' ? category.toLowerCase() : '';
    if (category.includes('good')) return 'rgba(0, 228, 0, 0.2)';
    if (category.includes('moderate')) return 'rgba(255, 255, 0, 0.2)';
    if (category.includes('sensitive')) return 'rgba(255, 126, 0, 0.2)';
    if (category.includes('unhealthy') && !category.includes('very')) return 'rgba(255, 0, 0, 0.2)';
    if (category.includes('very')) return 'rgba(143, 63, 151, 0.2)';
    return 'rgba(126, 0, 35, 0.2)';
}

// Utility to darken color for borders
function darkenColor(hex, percent) {
    // Convert hex to RGB
    let r = parseInt(hex.substring(1, 3), 16);
    let g = parseInt(hex.substring(3, 5), 16);
    let b = parseInt(hex.substring(5, 7), 16);
    
    // Reduce RGB values by percent
    r = Math.floor(r * (100 - percent) / 100);
    g = Math.floor(g * (100 - percent) / 100);
    b = Math.floor(b * (100 - percent) / 100);
    
    // Convert back to hex
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}
