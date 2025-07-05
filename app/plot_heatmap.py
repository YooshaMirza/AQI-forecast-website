import folium
import matplotlib.pyplot as plt
from folium import plugins
from datetime import datetime
from .model_loader import classify_aqi

def get_color_for_aqi(aqi):
    if aqi <= 50:
        return "#4CAF50"  # Green - Good
    elif aqi <= 100:
        return "#8BC34A"  # Light Green - Satisfactory
    elif aqi <= 200:
        return "#FFC107"  # Yellow - Moderate
    elif aqi <= 300:
        return "#FF9800"  # Orange - Poor
    elif aqi <= 400:
        return "#F44336"  # Red - Very Poor
    else:
        return "#9C27B0"  # Purple - Severe

def plot_heatmap(city_coords_aqi, center_city=None):
    cities, aqis = [], []
    center_lat, center_lon = 23.5937, 80.9629  # Default center (India)
    zoom_level = 5
    
    # If we have the center city in our data, center the map on it
    if center_city and center_city in city_coords_aqi:
        center_lat, center_lon, _ = city_coords_aqi[center_city]
        zoom_level = 10  # Zoom in more when focused on a specific city
    
    # Create the map with a more attractive tile
    tiles_options = [
        "CartoDB positron", 
        "CartoDB dark_matter", 
        "OpenStreetMap", 
        "Stamen Terrain"
    ]
    
    # Create the map with a more stylish background
    m = folium.Map(location=[center_lat, center_lon], 
                  zoom_start=zoom_level,
                  tiles="CartoDB positron")  # Cleaner map style
    
    # Add custom CSS for font and styling including animation for markers
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        .leaflet-container {
            font-family: 'Poppins', sans-serif !important;
        }
        .leaflet-popup-content {
            font-family: 'Poppins', sans-serif !important;
        }
        .leaflet-control {
            font-family: 'Poppins', sans-serif !important;
        }
        .leaflet-interactive {
            transition: all 0.3s ease;
        }
        .leaflet-interactive:hover {
            stroke-width: 4px !important;
            stroke-opacity: 1 !important;
            fill-opacity: 0.9 !important;
        }
        .leaflet-popup-content-wrapper {
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .leaflet-popup-tip {
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
    </style>
    """
    m.get_root().html.add_child(folium.Element(custom_css))
    
    # Add multiple tile layers for user to choose from
    folium.TileLayer('CartoDB positron', name='Light Theme').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Theme').add_to(m)
    folium.TileLayer('OpenStreetMap', name='Standard Map').add_to(m)
    folium.TileLayer('Stamen Terrain', name='Terrain').add_to(m)
    
    # Add default city if no data
    if not city_coords_aqi:
        # Add Delhi as a default city with a moderate AQI
        delhi_lat, delhi_lon = 28.6139, 77.2090
        delhi_aqi = 150
        folium.CircleMarker(
            location=[delhi_lat, delhi_lon],
            radius=15,
            popup=folium.Popup(f"<b>Delhi (Default)</b><br>AQI: {delhi_aqi}<br>Category: {classify_aqi(delhi_aqi)}", max_width=300),
            color="#000",
            weight=2,
            fill_color=get_color_for_aqi(delhi_aqi),
            fill=True,
            fill_opacity=0.7
        ).add_to(m)
        cities.append("Delhi (Default)")
        aqis.append(delhi_aqi)
        
    # Add user-provided cities
    for city, (lat, lon, aqi) in city_coords_aqi.items():
        # Main marker with popup
        color = get_color_for_aqi(aqi)
        radius = 20 if city == center_city else 10  # Make the searched city's marker bigger
        
        # Even more enhanced popup with better styling and info
        popup_html = f"""
        <div style="font-family: 'Poppins', Arial, sans-serif; padding: 16px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <h3 style="margin-bottom: 12px; color: #333; font-weight: 600; border-bottom: 2px solid {color}; padding-bottom: 8px;">{city.title()}</h3>
            <div style="background: linear-gradient(45deg, {color}, {color}dd); color: white; padding: 12px; border-radius: 8px; margin-bottom: 10px; text-align: center;">
                <span style="font-size: 32px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">{aqi}</span>
                <span style="display: block; font-size: 14px; margin-top: 5px;">AQI Value</span>
            </div>
            <div style="background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-top: 10px;">
                <p style="margin: 5px 0;"><b>Category:</b> <span style="font-weight: 600; color: {color}; padding: 3px 8px; background-color: {color}22; border-radius: 4px;">{classify_aqi(aqi)}</span></p>
                <p style="margin: 8px 0; font-size: 12px; color: #666;">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
        </div>
        """
        
        # Add the marker with enhanced styling
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=f"<b>{city.title()}</b>: AQI {aqi} • {classify_aqi(aqi)}",
            color="#000",
            weight=2,
            fill_color=color,
            fill=True,
            fill_opacity=0.85
        ).add_to(m)
        
        # For the searched city, add a more prominent marker with an outer circle
        if city == center_city:
            # Add multiple circles with decreasing opacity for a halo effect
            for i in range(3, 0, -1):
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius * (1 + i * 0.5),  # Progressively larger circles
                    color=color,
                    weight=2,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.1 / i,  # Decreasing opacity
                    opacity=0.3,
                    popup=None,
                    tooltip=None
                ).add_to(m)
            
            # Add a dashed circle for extra emphasis
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius * 2,  # Larger than the main marker
                color=color,
                weight=2,
                fill=False,
                dash_array='5, 10'  # Creates a dashed circle
            ).add_to(m)
            
            # Add a custom icon marker on top of the circle marker
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    icon_size=(20, 20),
                    icon_anchor=(10, 10),
                    html=f'''
                        <div style="
                            width: 10px;
                            height: 10px;
                            background-color: {color};
                            border: 2px solid white;
                            border-radius: 50%;
                            box-shadow: 0 0 5px #000;
                        "></div>
                    '''
                ),
                popup=None,
                tooltip=None
            ).add_to(m)
        
        cities.append(city)
        aqis.append(aqi)
    # Use absolute paths for saving files
    import os
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    
    # Make sure the static directory exists
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        
    heatmap_path = os.path.join(static_dir, "regional_heatmap.html")
    
    # Add more interactive features to the map
    folium.LayerControl().add_to(m)
    
    # Add an even more attractive title to the map
    title_text = f"Air Quality Map for {center_city.title()}" if center_city else "Air Quality Index Map"
    
    title_html = f'''
        <div style="position: fixed; 
                    top: 10px; 
                    left: 50px; 
                    width: 320px; 
                    z-index: 9999; 
                    font-size: 16px; 
                    font-family: 'Poppins', Arial, sans-serif;
                    background-color: rgba(255, 255, 255, 0.95);
                    color: #333;
                    text-align: center;
                    padding: 12px;
                    border-radius: 8px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                    border-left: 4px solid #4CAF50;">
            <div style="font-weight: 600; font-size: 18px; margin-bottom: 5px;">{title_text}</div>
            <div style="font-size: 14px; opacity: 0.8;">Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add a better styled legend
    legend_html = '''
        <div style="position: fixed; 
                    bottom: 30px; 
                    right: 30px; 
                    z-index: 9999; 
                    background-color: rgba(255, 255, 255, 0.95);
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                    font-family: 'Poppins', Arial, sans-serif;
                    font-size: 12px;
                    max-width: 220px;
                    border-top: 4px solid #2196F3;">
            <p style="text-align: center; margin: 0 0 8px 0; font-weight: 600; font-size: 14px; color: #333;">AQI Categories</p>
            <div style="margin-bottom: 6px; display: flex; align-items: center;">
                <span style="background-color: #4CAF50; display: inline-block; width: 15px; height: 15px; margin-right: 8px; border-radius: 3px;"></span>
                <span>Good (0-50)</span>
            </div>
            <div style="margin-bottom: 6px; display: flex; align-items: center;">
                <span style="background-color: #8BC34A; display: inline-block; width: 15px; height: 15px; margin-right: 8px; border-radius: 3px;"></span>
                <span>Satisfactory (51-100)</span>
            </div>
            <div style="margin-bottom: 6px; display: flex; align-items: center;">
                <span style="background-color: #FFC107; display: inline-block; width: 15px; height: 15px; margin-right: 8px; border-radius: 3px;"></span>
                <span>Moderate (101-200)</span>
            </div>
            <div style="margin-bottom: 6px; display: flex; align-items: center;">
                <span style="background-color: #FF9800; display: inline-block; width: 15px; height: 15px; margin-right: 8px; border-radius: 3px;"></span>
                <span>Poor (201-300)</span>
            </div>
            <div style="margin-bottom: 6px; display: flex; align-items: center;">
                <span style="background-color: #F44336; display: inline-block; width: 15px; height: 15px; margin-right: 8px; border-radius: 3px;"></span>
                <span>Very Poor (301-400)</span>
            </div>
            <div style="margin-bottom: 0; display: flex; align-items: center;">
                <span style="background-color: #9C27B0; display: inline-block; width: 15px; height: 15px; margin-right: 8px; border-radius: 3px;"></span>
                <span>Severe (400+)</span>
            </div>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the heatmap
    m.save(heatmap_path)
    print(f"Heatmap saved to {heatmap_path}")
