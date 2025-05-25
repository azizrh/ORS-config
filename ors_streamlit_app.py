# import streamlit as st
# import requests
# import json
# import folium
# from streamlit_folium import st_folium
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import numpy as np

# # Page configuration
# st.set_page_config(
#     page_title="OpenRouteService API Interface",
#     page_icon="🗺️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Initialize session state
# if 'base_url' not in st.session_state:
#     st.session_state.base_url = "http://localhost:8080/ors/v2"

# # Sidebar configuration
# st.sidebar.title("🗺️ ORS Configuration")
# base_url = st.sidebar.text_input(
#     "ORS Base URL", 
#     value=st.session_state.base_url,
#     help="Your local ORS instance URL"
# )
# st.session_state.base_url = base_url

# # API profiles
# PROFILES = [
#     "driving-car", "driving-hgv", "cycling-regular", "cycling-road", 
#     "cycling-mountain", "cycling-electric", "foot-walking", "foot-hiking", "wheelchair"
# ]

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="OpenRouteService API Interface",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'base_url' not in st.session_state:
    st.session_state.base_url = "http://localhost:8080/ors/v2"

# Sidebar configuration
st.sidebar.title("🗺️ ORS Configuration")
base_url = st.sidebar.text_input(
    "ORS Base URL",
    value=st.session_state.base_url,
    help="Your local ORS instance URL"
)
st.session_state.base_url = base_url

# Function to get available profiles from ORS
def get_available_profiles():
    """Get available profiles from ORS backend"""
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            profiles = []
            
            # Extract profile names from the status response
            if "profiles" in status_data:
                for profile_key, profile_data in status_data["profiles"].items():
                    if "profiles" in profile_data:
                        profile_name = profile_data["profiles"]
                        profiles.append(profile_name)
            
            return sorted(list(set(profiles))) if profiles else ["driving-car"]
        else:
            return ["driving-car"]  # Fallback
    except:
        return ["driving-car"]  # Fallback

# Get available profiles dynamically
PROFILES = get_available_profiles()

# Display available profiles in sidebar
st.sidebar.subheader("📋 Available Profiles")
for profile in PROFILES:
    st.sidebar.success(f"✅ {profile}")
st.sidebar.info(f"Total: {len(PROFILES)} profile(s)")

# Rest of your existing code continues here...

# Helper functions
def make_request(endpoint, params=None, data=None, method="GET"):
    """Make request to ORS API"""
    url = f"{base_url}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, headers=headers)
        else:
            response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return None, str(e)

def create_map(center=[52.520008, 13.404954], zoom=14):
    """Create a folium map"""
    m = folium.Map(location=center, zoom_start=zoom)
    return m

def add_markers_to_map(m, coordinates, labels=None, colors=None):
    """Add markers to map"""
    if not labels:
        labels = [f"Point {i+1}" for i in range(len(coordinates))]
    if not colors:
        colors = ['red', 'blue', 'green', 'purple', 'orange'] * (len(coordinates) // 5 + 1)
    
    for i, (coord, label) in enumerate(zip(coordinates, labels)):
        folium.Marker(
            location=[coord[1], coord[0]],  # lat, lon
            popup=label,
            icon=folium.Icon(color=colors[i % len(colors)])
        ).add_to(m)
    return m

def add_route_to_map(m, route_geometry):
    """Add route line to map"""
    if route_geometry and route_geometry.get("type") == "LineString":
        coordinates = route_geometry["coordinates"]
        # Convert to lat,lon format for folium
        route_coords = [[coord[1], coord[0]] for coord in coordinates]
        folium.PolyLine(
            route_coords, 
            color='blue', 
            weight=5, 
            opacity=0.8,
            popup="Route"
        ).add_to(m)
    return m

# Main interface
st.title("🗺️ OpenRouteService API Interface")
st.markdown("Streamlined interface for Routing, Isochrones, and Optimization APIs")

# Check API health
with st.container():
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔍 Check API Health"):
            health_data, error = make_request("health")
            if health_data:
                st.success("✅ API is healthy!")
                with st.expander("Health Details"):
                    st.json(health_data)
            else:
                st.error(f"❌ API Error: {error}")

# API Service Selection
service = st.selectbox(
    "🎯 Select ORS Service",
    ["Directions", "Isochrones"],#"Optimization"],
    help="Choose which ORS API service to use"
)

# Service-specific interfaces
# if service == "Directions":
#     st.header("🧭 Directions API")
#     st.markdown("Get routing directions between waypoints")
    
#     with st.container():
#         col1, col2 = st.columns([1, 1])
        
#         with col1:
#             st.subheader("Route Parameters")
#             profile = st.selectbox("Transportation Profile", PROFILES, index=0)
#             preference = st.selectbox("Route Preference", ["fastest", "shortest", "recommended"])
            
#             # Coordinate input
#             st.subheader("Waypoints")
#             num_waypoints = st.number_input("Number of waypoints", min_value=2, max_value=50, value=2)
            
#             coordinates = []
#             for i in range(num_waypoints):
#                 with st.expander(f"📍 Waypoint {i+1}", expanded=i < 2):
#                     col_lat, col_lon = st.columns(2)
#                     with col_lat:
#                         lat = st.number_input(
#                             f"Latitude", 
#                             value=-6.2446 + i*0.01, 
#                             key=f"lat_{i}",
#                             format="%.6f"
#                         )
#                     with col_lon:
#                         lon = st.number_input(
#                             f"Longitude", 
#                             value=106.8006 + i*0.01, 
#                             key=f"lon_{i}",
#                             format="%.6f"
#                         )
#                     coordinates.append([lon, lat])
            
#             # Advanced options
#             with st.expander("🔧 Advanced Options"):
#                 alternative_routes = st.number_input("Alternative routes", min_value=0, max_value=3, value=0)
#                 instructions = st.checkbox("Include turn-by-turn instructions", value=True)
#                 elevation = st.checkbox("Include elevation data", value=False)
#                 geometry_format = st.selectbox("Geometry format", ["geojson", "polyline", "encodedpolyline"])
                
#                 # Route restrictions
#                 st.subheader("Route Restrictions")
#                 avoid_borders = st.checkbox("Avoid country borders")
#                 avoid_tollways = st.checkbox("Avoid toll roads")
#                 avoid_highways = st.checkbox("Avoid highways")
#                 avoid_ferries = st.checkbox("Avoid ferries")
        
#         with col2:
#             st.subheader("📍 Route Preview")
#             m = create_map([coordinates[0][1], coordinates[0][0]])
#             m = add_markers_to_map(m, coordinates, [f"Waypoint {i+1}" for i in range(len(coordinates))])
#             map_data = st_folium(m, width=500, height=450)
            
#             if st.button("🚀 Calculate Route", type="primary"):
#                 request_body = {
#                     "coordinates": coordinates,
#                     "profile": profile,
#                     "preference": preference,
#                     "format": "json",
#                     "instructions": instructions,
#                     "elevation": elevation,
#                     "geometry_format": geometry_format
#                 }
                
#                 # Add route options
#                 options = {}
#                 avoid_features = []
#                 if avoid_borders:
#                     avoid_features.append("borders")
#                 if avoid_tollways:
#                     avoid_features.append("tollways")
#                 if avoid_highways:
#                     avoid_features.append("highways")
#                 if avoid_ferries:
#                     avoid_features.append("ferries")
                
#                 if avoid_features:
#                     options["avoid_features"] = avoid_features
                
#                 if options:
#                     request_body["options"] = options
                
#                 if alternative_routes > 0:
#                     request_body["alternative_routes"] = {"target_count": alternative_routes}
                
#                 with st.spinner("Calculating route..."):
#                     result, error = make_request("directions/" + profile, data=request_body, method="POST")
                
#                 if result:
#                     st.success("✅ Route calculated successfully!")
                    
#                     # Display route summary
#                     routes = result["routes"]
                    
#                     for route_idx, route in enumerate(routes):
#                         route_name = "Main Route" if route_idx == 0 else f"Alternative Route {route_idx}"
                        
#                         with st.expander(f"🛣️ {route_name}", expanded=route_idx == 0):
#                             summary = route["summary"]
                            
#                             # Route metrics
#                             col_dist, col_time, col_ascent = st.columns(3)
#                             with col_dist:
#                                 st.metric("Distance", f"{summary['distance']/1000:.2f} km")
#                             with col_time:
#                                 duration_hours = summary['duration'] // 3600
#                                 duration_mins = (summary['duration'] % 3600) // 60
#                                 if duration_hours > 0:
#                                     time_str = f"{duration_hours}h {duration_mins}m"
#                                 else:
#                                     time_str = f"{duration_mins}m"
#                                 st.metric("Duration", time_str)
#                             with col_ascent:
#                                 if "ascent" in summary:
#                                     st.metric("Total Ascent", f"{summary['ascent']:.0f} m")
                            
#                             # Route visualization
#                             st.subheader("Route Map")
#                             route_map = create_map([coordinates[0][1], coordinates[0][0]])
#                             route_map = add_markers_to_map(route_map, coordinates, [f"Waypoint {i+1}" for i in range(len(coordinates))])
#                             route_map = add_route_to_map(route_map, route.get("geometry"))
#                             st_folium(route_map, width=700, height=400, key=f"route_map_{route_idx}")
                            
#                             # Show instructions if available
#                             if "segments" in route and instructions:
#                                 st.subheader("📋 Turn-by-turn Instructions")
#                                 instructions_data = []
#                                 step_number = 1
                                
#                                 for segment_idx, segment in enumerate(route["segments"]):
#                                     if "steps" in segment:
#                                         for step in segment["steps"]:
#                                             instructions_data.append({
#                                                 "Step": step_number,
#                                                 "Instruction": step.get("instruction", "Continue"),
#                                                 "Distance": f"{step.get('distance', 0)/1000:.2f} km",
#                                                 "Duration": f"{step.get('duration', 0)/60:.1f} min"
#                                             })
#                                             step_number += 1
                                
#                                 if instructions_data:
#                                     df_instructions = pd.DataFrame(instructions_data)
#                                     st.dataframe(df_instructions, use_container_width=True, hide_index=True)
                            
#                             # Elevation profile if available
#                             if elevation and "elevation" in route:
#                                 st.subheader("📈 Elevation Profile")
#                                 elevation_data = route["elevation"]
                                
#                                 # Create elevation chart
#                                 distances = [point[0] for point in elevation_data]
#                                 elevations = [point[1] for point in elevation_data]
                                
#                                 fig = go.Figure()
#                                 fig.add_trace(go.Scatter(
#                                     x=distances,
#                                     y=elevations,
#                                     mode='lines',
#                                     name='Elevation',
#                                     line=dict(color='brown', width=2),
#                                     fill='tonexty'
#                                 ))
                                
#                                 fig.update_layout(
#                                     title="Route Elevation Profile",
#                                     xaxis_title="Distance (m)",
#                                     yaxis_title="Elevation (m)",
#                                     showlegend=False,
#                                     height=300
#                                 )
                                
#                                 st.plotly_chart(fig, use_container_width=True)
                    
#                     # Show full response in expander
#                     with st.expander("📄 Full API Response"):
#                         st.json(result)
#                 else:
#                     st.error(f"❌ Error: {error}")

# if service == "Directions":
#     st.header("🧭 Directions API")
#     st.markdown("Get routing directions between waypoints")
    
#     # Initialize session state for persistent results
#     if 'directions_results' not in st.session_state:
#         st.session_state.directions_results = None
#     if 'directions_coordinates' not in st.session_state:
#         st.session_state.directions_coordinates = []
#     if 'directions_params' not in st.session_state:
#         st.session_state.directions_params = {}
    
#     with st.container():
#         col1, col2 = st.columns([1, 1])
        
#         with col1:
#             st.subheader("Route Parameters")
#             profile = st.selectbox("Transportation Profile", PROFILES, index=0)
            
#             # Coordinate input
#             st.subheader("Waypoints")
#             num_waypoints = st.number_input("Number of waypoints", min_value=2, max_value=50, value=2)
            
#             coordinates = []
#             for i in range(num_waypoints):
#                 with st.expander(f"📍 Waypoint {i+1}", expanded=i < 2):
#                     col_lat, col_lon = st.columns(2)
#                     with col_lat:
#                         lat = st.number_input(
#                             f"Latitude", 
#                             value=-6.2446 + i*0.01, 
#                             key=f"lat_{i}",
#                             format="%.6f"
#                         )
#                     with col_lon:
#                         lon = st.number_input(
#                             f"Longitude", 
#                             value=106.8006 + i*0.01, 
#                             key=f"lon_{i}",
#                             format="%.6f"
#                         )
#                     coordinates.append([lon, lat])
            
#             # Advanced options
#             with st.expander("🔧 Advanced Options"):
#                 alternative_routes = st.number_input("Alternative routes", min_value=0, max_value=3, value=0)
#                 instructions = st.checkbox("Include turn-by-turn instructions", value=True)
#                 elevation = st.checkbox("Include elevation data", value=False)
#                 geometry = st.checkbox("Include route geometry", value=True)
                
#                 # Route restrictions
#                 st.subheader("Route Restrictions")
#                 avoid_borders = st.checkbox("Avoid country borders")
#                 avoid_tollways = st.checkbox("Avoid toll roads")
#                 avoid_highways = st.checkbox("Avoid highways")
#                 avoid_ferries = st.checkbox("Avoid ferries")
        
#         with col2:
#             st.subheader("📍 Route Preview")
#             if coordinates:
#                 m = create_map([coordinates[0][1], coordinates[0][0]])
#                 m = add_markers_to_map(m, coordinates, [f"Waypoint {i+1}" for i in range(len(coordinates))])
#                 map_data = st_folium(m, width=500, height=450, key="directions_preview_map")
    
#     # Separate container for buttons to prevent rerun issues
#     st.divider()
    
#     col_btn, col_clear = st.columns([1, 4])
#     with col_btn:
#         calculate_clicked = st.button("🚀 Calculate Route", type="primary", key="calculate_route")
#     with col_clear:
#         if st.button("🗑️ Clear Results", key="clear_directions"):
#             st.session_state.directions_results = None
#             st.session_state.directions_coordinates = []
#             st.session_state.directions_params = {}
#             st.rerun()
    
#     # Process calculation only when button is clicked
#     if calculate_clicked:
#         # Build request body with correct parameters for ORS v8.0.0
#         request_body = {
#             "coordinates": coordinates,
#             "format": "geojson",  # Changed from geometry_format
#             "instructions": instructions,
#             "geometry": geometry,
#             "elevation": elevation
#         }
        
#         # Add route options
#         options = {}
#         avoid_features = []
#         if avoid_borders:
#             avoid_features.append("borders")
#         if avoid_tollways:
#             avoid_features.append("tollways")
#         if avoid_highways:
#             avoid_features.append("highways")
#         if avoid_ferries:
#             avoid_features.append("ferries")
        
#         if avoid_features:
#             options["avoid_features"] = avoid_features
        
#         if options:
#             request_body["options"] = options
        
#         if alternative_routes > 0:
#             request_body["alternative_routes"] = {"target_count": alternative_routes}
        
#         with st.spinner("Calculating route..."):
#             result, error = make_request(f"directions/{profile}", data=request_body, method="POST")
        
#         if result:
#             # Store results in session state
#             st.session_state.directions_results = result
#             st.session_state.directions_coordinates = coordinates
#             st.session_state.directions_params = {
#                 "profile": profile,
#                 "instructions": instructions,
#                 "geometry": geometry,
#                 "elevation": elevation
#             }
#             st.success("✅ Route calculated successfully!")
#         else:
#             st.error(f"❌ Error: {error}")
    
#     # Display results if they exist in session state
#     if st.session_state.directions_results is not None:
#         st.divider()
        
#         result = st.session_state.directions_results
#         coordinates = st.session_state.directions_coordinates
#         params = st.session_state.directions_params
        
#         # Debug: Show what's actually in the result
#         with st.expander("🔍 Debug - Response Structure"):
#             st.write(f"Response type: {type(result)}")
#             st.write(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
#         # Try different possible response structures
#         routes = []
#         if "routes" in result:
#             routes = result["routes"]
#             st.write(f"✅ Found 'routes' key with {len(routes)} route(s)")
#         elif "features" in result:
#             # GeoJSON format response
#             routes = result["features"]
#             st.write(f"✅ Found 'features' key with {len(routes)} feature(s)")
#         elif isinstance(result, dict):
#             # Single route response
#             routes = [result]
#             st.write("✅ Treating entire response as single route")
        
#         if not routes:
#             st.warning("⚠️ No routes found in the response")
#             with st.expander("🔍 Full Response for Debugging"):
#                 st.json(result)
#         else:
#             # Display route summary
#             for route_idx, route in enumerate(routes):
#                 route_name = "Main Route" if route_idx == 0 else f"Alternative Route {route_idx}"
                
#                 with st.expander(f"🛣️ {route_name}", expanded=route_idx == 0):
#                     # Handle different response formats
#                     if "properties" in route:
#                         # GeoJSON feature format
#                         summary = route["properties"].get("summary", {})
#                         segments = route["properties"].get("segments", [])
#                         geometry_data = route.get("geometry", {})
#                     else:
#                         # Direct route format
#                         summary = route.get("summary", {})
#                         segments = route.get("segments", [])
#                         geometry_data = route.get("geometry", {})
                    
#                     # Debug info as toggle instead of nested expander
#                     show_debug = st.checkbox(f"🔍 Show debug info for Route {route_idx + 1}", key=f"debug_{route_idx}")
#                     if show_debug:
#                         st.write(f"**Route keys:** {list(route.keys())}")
#                         if summary:
#                             st.write(f"**Summary keys:** {list(summary.keys())}")
#                         if geometry_data:
#                             st.write(f"**Geometry type:** {type(geometry_data)}")
#                             if isinstance(geometry_data, dict):
#                                 st.write(f"**Geometry keys:** {list(geometry_data.keys())}")
                    
#                     # Route metrics
#                     col_dist, col_time, col_ascent = st.columns(3)
#                     with col_dist:
#                         distance = summary.get('distance', 0)
#                         st.metric("Distance", f"{distance/1000:.2f} km" if distance else "N/A")
#                     with col_time:
#                         duration = summary.get('duration', 0)
#                         if duration:
#                             duration_hours = duration // 3600
#                             duration_mins = (duration % 3600) // 60
#                             if duration_hours > 0:
#                                 time_str = f"{duration_hours}h {duration_mins}m"
#                             else:
#                                 time_str = f"{duration_mins}m"
#                             st.metric("Duration", time_str)
#                         else:
#                             st.metric("Duration", "N/A")
#                     with col_ascent:
#                         ascent = summary.get('ascent', None)
#                         if ascent is not None:
#                             st.metric("Total Ascent", f"{ascent:.0f} m")
#                         else:
#                             st.metric("Total Ascent", "N/A")
                    
#                     # Route visualization (temporarily disabled for debugging)
#                     if params.get("geometry") and coordinates:
#                         st.subheader("🗺️ Route Map")
#                         route_map = create_map([coordinates[0][1], coordinates[0][0]])
#                         route_map = add_markers_to_map(route_map, coordinates, [f"Waypoint {i+1}" for i in range(len(coordinates))])
                        
#                         st.info("📍 Showing waypoints only (route line disabled for debugging)")
                        
#                         st_folium(route_map, width=700, height=400, key=f"route_map_{route_idx}")
                    
#                     # Show instructions if available
#                     if params.get("instructions") and segments:
#                         st.subheader("📋 Turn-by-turn Instructions")
#                         instructions_data = []
#                         step_number = 1
                        
#                         for segment_idx, segment in enumerate(segments):
#                             if "steps" in segment:
#                                 for step in segment["steps"]:
#                                     instructions_data.append({
#                                         "Step": step_number,
#                                         "Instruction": step.get("instruction", "Continue"),
#                                         "Distance": f"{step.get('distance', 0)/1000:.2f} km",
#                                         "Duration": f"{step.get('duration', 0)/60:.1f} min"
#                                     })
#                                     step_number += 1
                        
#                         if instructions_data:
#                             df_instructions = pd.DataFrame(instructions_data)
#                             st.dataframe(df_instructions, use_container_width=True, hide_index=True)
#                         else:
#                             st.info("No turn-by-turn instructions available for this route.")
#                     elif params.get("instructions"):
#                         st.info("Turn-by-turn instructions were requested but not available in the response.")
            
#             # Show full response in expander
#             with st.expander("📄 Full API Response"):
#                 st.json(result)

if service == "Directions":
    st.header("🧭 Directions API")
    st.markdown("Get routing directions between waypoints")
    
    # Initialize session state for persistent results
    if 'directions_results' not in st.session_state:
        st.session_state.directions_results = None
    if 'directions_coordinates' not in st.session_state:
        st.session_state.directions_coordinates = []
    if 'directions_params' not in st.session_state:
        st.session_state.directions_params = {}
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Route Parameters")
            profile = st.selectbox("Transportation Profile", PROFILES, index=0)
            
            # Coordinate input
            st.subheader("Waypoints")
            num_waypoints = st.number_input("Number of waypoints", min_value=2, max_value=50, value=2)
            
            coordinates = []
            for i in range(num_waypoints):
                with st.expander(f"📍 Waypoint {i+1}", expanded=i < 2):
                    col_lat, col_lon = st.columns(2)
                    with col_lat:
                        lat = st.number_input(
                            f"Latitude", 
                            value=-6.2446 + i*0.01, 
                            key=f"lat_{i}",
                            format="%.6f"
                        )
                    with col_lon:
                        lon = st.number_input(
                            f"Longitude", 
                            value=106.8006 + i*0.01, 
                            key=f"lon_{i}",
                            format="%.6f"
                        )
                    coordinates.append([lon, lat])
            
            # Advanced options
            with st.expander("🔧 Advanced Options"):
                alternative_routes = st.number_input("Alternative routes", min_value=0, max_value=3, value=0)
                instructions = st.checkbox("Include turn-by-turn instructions", value=True)
                elevation = st.checkbox("Include elevation data", value=False)
                geometry = st.checkbox("Include route geometry", value=True)
                
                # Route restrictions
                st.subheader("Route Restrictions")
                avoid_borders = st.checkbox("Avoid country borders")
                avoid_tollways = st.checkbox("Avoid toll roads")
                avoid_highways = st.checkbox("Avoid highways")
                avoid_ferries = st.checkbox("Avoid ferries")
        
        with col2:
            st.subheader("📍 Route Preview")
            if coordinates:
                m = create_map([coordinates[0][1], coordinates[0][0]])
                m = add_markers_to_map(m, coordinates, [f"Waypoint {i+1}" for i in range(len(coordinates))])
                map_data = st_folium(m, width=500, height=450, key="directions_preview_map")
    
    # Separate container for buttons to prevent rerun issues
    st.divider()
    
    col_btn, col_clear = st.columns([1, 4])
    with col_btn:
        calculate_clicked = st.button("🚀 Calculate Route", type="primary", key="calculate_route")
    with col_clear:
        if st.button("🗑️ Clear Results", key="clear_directions"):
            st.session_state.directions_results = None
            st.session_state.directions_coordinates = []
            st.session_state.directions_params = {}
            st.rerun()
    
    # Process calculation only when button is clicked
    if calculate_clicked:
        # Build request body with correct parameters for ORS v8.0.0
        request_body = {
            "coordinates": coordinates,
            "format": "geojson",  # This should return proper GeoJSON
            "instructions": instructions,
            "geometry": geometry,
            "elevation": elevation
        }
        
        # Add route options
        options = {}
        avoid_features = []
        if avoid_borders:
            avoid_features.append("borders")
        if avoid_tollways:
            avoid_features.append("tollways")
        if avoid_highways:
            avoid_features.append("highways")
        if avoid_ferries:
            avoid_features.append("ferries")
        
        if avoid_features:
            options["avoid_features"] = avoid_features
        
        if options:
            request_body["options"] = options
        
        if alternative_routes > 0:
            request_body["alternative_routes"] = {"target_count": alternative_routes}
        
        with st.spinner("Calculating route..."):
            result, error = make_request(f"directions/{profile}", data=request_body, method="POST")
        
        if result:
            # Store results in session state
            st.session_state.directions_results = result
            st.session_state.directions_coordinates = coordinates
            st.session_state.directions_params = {
                "profile": profile,
                "instructions": instructions,
                "geometry": geometry,
                "elevation": elevation
            }
            st.success("✅ Route calculated successfully!")
        else:
            st.error(f"❌ Error: {error}")
    
    # Display results if they exist in session state
    if st.session_state.directions_results is not None:
        st.divider()
        
        result = st.session_state.directions_results
        coordinates = st.session_state.directions_coordinates
        params = st.session_state.directions_params
        
        # Debug: Show what's actually in the result
        with st.expander("🔍 Debug - Response Structure"):
            st.write(f"Response type: {type(result)}")
            st.write(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Try different possible response structures
        routes = []
        if "routes" in result:
            routes = result["routes"]
            st.write(f"✅ Found 'routes' key with {len(routes)} route(s)")
        elif "features" in result:
            # GeoJSON format response
            routes = result["features"]
            st.write(f"✅ Found 'features' key with {len(routes)} feature(s)")
        elif isinstance(result, dict):
            # Single route response
            routes = [result]
            st.write("✅ Treating entire response as single route")
        
        if not routes:
            st.warning("⚠️ No routes found in the response")
            with st.expander("🔍 Full Response for Debugging"):
                st.json(result)
        else:
            # Display route summary
            for route_idx, route in enumerate(routes):
                route_name = "Main Route" if route_idx == 0 else f"Alternative Route {route_idx}"
                
                with st.expander(f"🛣️ {route_name}", expanded=route_idx == 0):
                    # Handle different response formats
                    if "properties" in route:
                        # GeoJSON feature format
                        summary = route["properties"].get("summary", {})
                        segments = route["properties"].get("segments", [])
                        geometry_data = route.get("geometry", {})
                    else:
                        # Direct route format
                        summary = route.get("summary", {})
                        segments = route.get("segments", [])
                        geometry_data = route.get("geometry", {})
                    
                    # Debug info as toggle instead of nested expander
                    show_debug = st.checkbox(f"🔍 Show debug info for Route {route_idx + 1}", key=f"debug_{route_idx}")
                    if show_debug:
                        st.write(f"**Route keys:** {list(route.keys())}")
                        if summary:
                            st.write(f"**Summary keys:** {list(summary.keys())}")
                        if geometry_data:
                            st.write(f"**Geometry type:** {type(geometry_data)}")
                            if isinstance(geometry_data, dict):
                                st.write(f"**Geometry keys:** {list(geometry_data.keys())}")
                    
                    # Route metrics
                    col_dist, col_time, col_ascent = st.columns(3)
                    with col_dist:
                        distance = summary.get('distance', 0)
                        st.metric("Distance", f"{distance/1000:.2f} km" if distance else "N/A")
                    with col_time:
                        duration = summary.get('duration', 0)
                        if duration:
                            duration_hours = duration // 3600
                            duration_mins = (duration % 3600) // 60
                            if duration_hours > 0:
                                time_str = f"{duration_hours}h {duration_mins}m"
                            else:
                                time_str = f"{duration_mins}m"
                            st.metric("Duration", time_str)
                        else:
                            st.metric("Duration", "N/A")
                    with col_ascent:
                        ascent = summary.get('ascent', None)
                        if ascent is not None:
                            st.metric("Total Ascent", f"{ascent:.0f} m")
                        else:
                            st.metric("Total Ascent", "N/A")
                    
                    # Route visualization
                    if params.get("geometry") and coordinates:
                        st.subheader("🗺️ Route Map")
                        route_map = create_map([coordinates[0][1], coordinates[0][0]])
                        route_map = add_markers_to_map(route_map, coordinates, [f"Waypoint {i+1}" for i in range(len(coordinates))])
                        
                        # Add route geometry with error handling
                        if geometry_data:
                            try:
                                route_coords = None
                                
                                # Handle different geometry formats
                                if isinstance(geometry_data, str):
                                    # Encoded polyline string - need to decode
                                    try:
                                        import polyline
                                        decoded_coords = polyline.decode(geometry_data)
                                        route_coords = decoded_coords  # Already in [lat, lon] format
                                        st.success("✅ Decoded polyline successfully!")
                                    except ImportError:
                                        st.error("❌ Polyline library not installed. Run: pip install polyline")
                                    except Exception as decode_error:
                                        st.error(f"❌ Failed to decode polyline: {str(decode_error)}")
                                        if show_debug:
                                            st.write("**Encoded polyline:**")
                                            st.code(geometry_data[:100] + "..." if len(geometry_data) > 100 else geometry_data)
                                
                                elif isinstance(geometry_data, dict) and "coordinates" in geometry_data:
                                    # GeoJSON LineString format
                                    coords = geometry_data["coordinates"]
                                    if coords and isinstance(coords[0], list):
                                        # Convert [lon, lat] to [lat, lon] for folium
                                        route_coords = [[coord[1], coord[0]] for coord in coords]
                                        st.success("✅ Using GeoJSON coordinates!")
                                
                                elif isinstance(geometry_data, list):
                                    # Direct array of coordinates
                                    if geometry_data and isinstance(geometry_data[0], list):
                                        # Convert [lon, lat] to [lat, lon] for folium
                                        route_coords = [[coord[1], coord[0]] for coord in geometry_data]
                                        st.success("✅ Using direct coordinates!")
                                
                                # Draw the route if we have coordinates
                                if route_coords:
                                    folium.PolyLine(
                                        locations=route_coords,
                                        color='blue',
                                        weight=4,
                                        opacity=0.8,
                                        popup="Route"
                                    ).add_to(route_map)
                                    st.success(f"✅ Route line displayed with {len(route_coords)} points!")
                                else:
                                    st.warning("⚠️ Could not extract route coordinates")
                                    
                            except Exception as e:
                                st.error(f"❌ Error displaying route: {str(e)}")
                                if show_debug:
                                    st.write("**Geometry data:**")
                                    st.write(f"Type: {type(geometry_data)}")
                                    if isinstance(geometry_data, str):
                                        st.code(geometry_data[:200] + "..." if len(geometry_data) > 200 else geometry_data)
                                    else:
                                        st.json(geometry_data)
                        else:
                            st.info("📍 No route geometry available - showing waypoints only")
                        
                        st_folium(route_map, width=700, height=400, key=f"route_map_{route_idx}")
                    
                    # Show instructions if available
                    if params.get("instructions") and segments:
                        st.subheader("📋 Turn-by-turn Instructions")
                        instructions_data = []
                        step_number = 1
                        
                        for segment_idx, segment in enumerate(segments):
                            if "steps" in segment:
                                for step in segment["steps"]:
                                    instructions_data.append({
                                        "Step": step_number,
                                        "Instruction": step.get("instruction", "Continue"),
                                        "Distance": f"{step.get('distance', 0)/1000:.2f} km",
                                        "Duration": f"{step.get('duration', 0)/60:.1f} min"
                                    })
                                    step_number += 1
                        
                        if instructions_data:
                            df_instructions = pd.DataFrame(instructions_data)
                            st.dataframe(df_instructions, use_container_width=True, hide_index=True)
                        else:
                            st.info("No turn-by-turn instructions available for this route.")
                    elif params.get("instructions"):
                        st.info("Turn-by-turn instructions were requested but not available in the response.")
            
            # Show full response in expander
            with st.expander("📄 Full API Response"):
                st.json(result)

# elif service == "Isochrones":
#     st.header("⏰ Isochrones API")
#     st.markdown("Generate reachability areas (isochrones) from locations")
    
#     with st.container():
#         col1, col2 = st.columns([1, 1])
        
#         with col1:
#             st.subheader("Isochrone Parameters")
#             profile = st.selectbox("Transportation Profile", PROFILES, index=0, key="iso_profile")
            
#             # Location input
#             st.subheader("📍 Source Locations")
#             num_locations = st.number_input("Number of locations", min_value=1, max_value=5, value=1)
            
#             locations = []
#             for i in range(num_locations):
#                 with st.expander(f"Location {i+1}", expanded=i == 0):
#                     col_lat, col_lon = st.columns(2)
#                     with col_lat:
#                         lat = st.number_input(
#                             f"Latitude", 
#                             value=52.520008 + i*0.005, 
#                             key=f"iso_lat_{i}",
#                             format="%.6f"
#                         )
#                     with col_lon:
#                         lon = st.number_input(
#                             f"Longitude", 
#                             value=13.404954 + i*0.005, 
#                             key=f"iso_lon_{i}",
#                             format="%.6f"
#                         )
#                     locations.append([lon, lat])
            
#             # Range settings
#             st.subheader("⏱️ Range Configuration")
#             range_type = st.selectbox("Range type", ["time", "distance"])
            
#             if range_type == "time":
#                 st.write("**Time ranges (minutes)**")
#                 col_r1, col_r2, col_r3 = st.columns(3)
#                 with col_r1:
#                     range1 = st.number_input("Range 1", value=5, min_value=1, max_value=60)
#                 with col_r2:
#                     range2 = st.number_input("Range 2", value=10, min_value=1, max_value=60)
#                 with col_r3:
#                     range3 = st.number_input("Range 3", value=15, min_value=1, max_value=60)
                
#                 # Convert to seconds
#                 range_list = [r * 60 for r in [range1, range2, range3] if r > 0]
#                 st.caption(f"Isochrones for: {', '.join([f'{r//60} min' for r in range_list])}")
#             else:
#                 st.write("**Distance ranges (kilometers)**")
#                 col_r1, col_r2, col_r3 = st.columns(3)
#                 with col_r1:
#                     range1 = st.number_input("Range 1", value=1.0, min_value=0.1, max_value=50.0, step=0.1)
#                 with col_r2:
#                     range2 = st.number_input("Range 2", value=2.0, min_value=0.1, max_value=50.0, step=0.1)
#                 with col_r3:
#                     range3 = st.number_input("Range 3", value=3.0, min_value=0.1, max_value=50.0, step=0.1)
                
#                 # Convert to meters
#                 range_list = [int(r * 1000) for r in [range1, range2, range3] if r > 0]
#                 st.caption(f"Isochrones for: {', '.join([f'{r/1000:.1f} km' for r in range_list])}")
            
#             # Advanced options
#             with st.expander("🔧 Advanced Options"):
#                 smoothing = st.slider("Smoothing factor", min_value=0.0, max_value=100.0, value=25.0, step=5.0)
#                 location_type = st.selectbox("Location type", ["start", "destination"])
                
#                 # Area units
#                 area_units = st.selectbox("Area calculation units", ["m", "km", "mi"])
        
#         with col2:
#             st.subheader("📍 Location Preview")
#             if locations:
#                 center_lat = sum(loc[1] for loc in locations) / len(locations)
#                 center_lon = sum(loc[0] for loc in locations) / len(locations)
                
#                 m = create_map([center_lat, center_lon])
#                 m = add_markers_to_map(m, locations, [f"Source {i+1}" for i in range(len(locations))])
#                 map_data = st_folium(m, width=500, height=450)
            
#             if st.button("🎯 Generate Isochrones", type="primary"):
#                 request_body = {
#                     "locations": locations,
#                     "range": [max(range_list)], #range_list,
#                     "range_type": range_type,
#                     "smoothing": smoothing,
#                     "location_type": location_type,
#                     "area_units": area_units
#                 }
                
#                 with st.spinner("Generating isochrones..."):
#                     result, error = make_request(f"isochrones/{profile}", data=request_body, method="POST")
                
#                 if result:
#                     st.success("✅ Isochrones generated successfully!")
                    
#                     # Display statistics
#                     features = result["features"]
#                     st.subheader(f"📊 Generated {len(features)} isochrone(s)")
                    
#                     # Create summary table
#                     iso_data = []
#                     for feature in features:
#                         props = feature["properties"]
#                         range_value = props.get('value', 0)
                        
#                         # Format range display
#                         if range_type == "time":
#                             range_display = f"{range_value//60} minutes"
#                         else:
#                             range_display = f"{range_value/1000:.1f} km"
                        
#                         iso_data.append({
#                             "Range": range_display,
#                             "Area": f"{props.get('area', 0):.2f} {area_units}²",
#                             "Center": f"({props.get('center', [0, 0])[1]:.4f}, {props.get('center', [0, 0])[0]:.4f})"
#                         })
                    
#                     df_iso = pd.DataFrame(iso_data)
#                     st.dataframe(df_iso, use_container_width=True, hide_index=True)
                    
#                     # Visualization
#                     st.subheader("🗺️ Isochrone Visualization")
#                     iso_map = create_map([center_lat, center_lon])
                    
#                     # Add source markers
#                     iso_map = add_markers_to_map(iso_map, locations, [f"Source {i+1}" for i in range(len(locations))])
                    
#                     # Add isochrone polygons
#                     colors = ['red', 'orange', 'yellow', 'green', 'blue']
#                     for idx, feature in enumerate(features):
#                         if feature["geometry"]["type"] == "Polygon":
#                             coordinates = feature["geometry"]["coordinates"][0]
#                             # Convert to lat,lon for folium
#                             polygon_coords = [[coord[1], coord[0]] for coord in coordinates]
                            
#                             range_value = feature["properties"].get('value', 0)
#                             if range_type == "time":
#                                 popup_text = f"Reachable in {range_value//60} minutes"
#                             else:
#                                 popup_text = f"Reachable within {range_value/1000:.1f} km"
                            
#                             folium.Polygon(
#                                 polygon_coords,
#                                 color=colors[idx % len(colors)],
#                                 weight=2,
#                                 opacity=0.8,
#                                 fillColor=colors[idx % len(colors)],
#                                 fillOpacity=0.2,
#                                 popup=popup_text
#                             ).add_to(iso_map)
                    
#                     st_folium(iso_map, width=700, height=500)
                    
#                     with st.expander("📄 Full API Response"):
#                         st.json(result)
#                 else:
#                     st.error(f"❌ Error: {error}")
elif service == "Isochrones":
    st.header("⏰ Isochrones API")
    st.markdown("Generate reachability areas (isochrones) from locations")
    
    # Initialize session state for persistent results
    if 'isochrone_results' not in st.session_state:
        st.session_state.isochrone_results = None
    if 'isochrone_locations' not in st.session_state:
        st.session_state.isochrone_locations = []
    if 'isochrone_params' not in st.session_state:
        st.session_state.isochrone_params = {}
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Isochrone Parameters")
            profile = st.selectbox("Transportation Profile", PROFILES, index=0, key="iso_profile")
            
            # Location input
            st.subheader("📍 Source Locations")
            num_locations = st.number_input("Number of locations", min_value=1, max_value=5, value=1)
            
            locations = []
            for i in range(num_locations):
                with st.expander(f"Location {i+1}", expanded=i == 0):
                    col_lat, col_lon = st.columns(2)
                    with col_lat:
                        lat = st.number_input(
                            f"Latitude", 
                            value=-6.2446 + i*0.005,  # Default to Jakarta
                            key=f"iso_lat_{i}",
                            format="%.6f"
                        )
                    with col_lon:
                        lon = st.number_input(
                            f"Longitude", 
                            value=106.8006 + i*0.005,  # Default to Jakarta
                            key=f"iso_lon_{i}",
                            format="%.6f"
                        )
                    locations.append([lon, lat])
            
            # Range settings
            st.subheader("⏱️ Range Configuration")
            range_type = st.selectbox("Range type", ["time", "distance"])
            
            if range_type == "time":
                st.write("**Time ranges (minutes)**")
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    range1 = st.number_input("Range 1", value=5, min_value=1, max_value=60)
                with col_r2:
                    range2 = st.number_input("Range 2", value=10, min_value=1, max_value=60)
                with col_r3:
                    range3 = st.number_input("Range 3", value=15, min_value=1, max_value=60)
                
                # Convert to seconds
                range_list = [r * 60 for r in [range1, range2, range3] if r > 0]
                st.caption(f"Isochrones for: {', '.join([f'{r//60} min' for r in range_list])}")
            else:
                st.write("**Distance ranges (kilometers)**")
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    range1 = st.number_input("Range 1", value=1.0, min_value=0.1, max_value=50.0, step=0.1)
                with col_r2:
                    range2 = st.number_input("Range 2", value=2.0, min_value=0.1, max_value=50.0, step=0.1)
                with col_r3:
                    range3 = st.number_input("Range 3", value=3.0, min_value=0.1, max_value=50.0, step=0.1)
                
                # Convert to meters
                range_list = [int(r * 1000) for r in [range1, range2, range3] if r > 0]
                st.caption(f"Isochrones for: {', '.join([f'{r/1000:.1f} km' for r in range_list])}")
            
            # Advanced options
            with st.expander("🔧 Advanced Options"):
                smoothing = st.slider("Smoothing factor", min_value=0.0, max_value=100.0, value=25.0, step=5.0)
                location_type = st.selectbox("Location type", ["start", "destination"])
                area_units = st.selectbox("Area calculation units", ["m", "km", "mi"])
        
        with col2:
            st.subheader("📍 Location Preview")
            if locations:
                center_lat = sum(loc[1] for loc in locations) / len(locations)
                center_lon = sum(loc[0] for loc in locations) / len(locations)
                
                m = create_map([center_lat, center_lon])
                m = add_markers_to_map(m, locations, [f"Source {i+1}" for i in range(len(locations))])
                map_data = st_folium(m, width=500, height=450, key="preview_map")
    
    # Separate container for the generate button to prevent rerun issues
    st.divider()
    
    # Generate button in its own container
    col_btn, col_clear = st.columns([1, 4])
    with col_btn:
        generate_clicked = st.button("🎯 Generate Isochrones", type="primary", key="generate_iso")
    with col_clear:
        if st.button("🗑️ Clear Results", key="clear_iso"):
            st.session_state.isochrone_results = None
            st.session_state.isochrone_locations = []
            st.session_state.isochrone_params = {}
            st.rerun()
    
    # Process generation only when button is clicked
    if generate_clicked:
        # Sequential requests for each range to avoid interval limit
        all_features = []
        successful_requests = 0
        total_requests = len(range_list)
        
        # Create progress bar
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        with st.spinner("Generating isochrones..."):
            for idx, range_value in enumerate(range_list):
                # Update progress
                progress = (idx + 1) / total_requests
                progress_bar.progress(progress)
                
                if range_type == "time":
                    status_text.text(f"Generating {range_value//60} minute isochrone... ({idx+1}/{total_requests})")
                else:
                    status_text.text(f"Generating {range_value/1000:.1f} km isochrone... ({idx+1}/{total_requests})")
                
                # Request single isochrone
                request_body = {
                    "locations": locations,
                    "range": [range_value],  # Single range value
                    "range_type": range_type,
                    "smoothing": smoothing,
                    "location_type": location_type,
                    "area_units": area_units
                }
                
                result, error = make_request(f"isochrones/{profile}", data=request_body, method="POST")
                
                if result and "features" in result:
                    # Add features from this request to the collection
                    all_features.extend(result["features"])
                    successful_requests += 1
                else:
                    st.warning(f"⚠️ Failed to generate isochrone for range {range_value}: {error}")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        progress_container.empty()
        
        if successful_requests > 0:
            # Store results in session state
            combined_result = {
                "type": "FeatureCollection",
                "features": all_features,
                "bbox": result.get("bbox", []) if result else [],
                "info": result.get("info", {}) if result else {}
            }
            
            st.session_state.isochrone_results = combined_result
            st.session_state.isochrone_locations = locations
            st.session_state.isochrone_params = {
                "range_type": range_type,
                "area_units": area_units,
                "successful_requests": successful_requests,
                "total_requests": total_requests
            }
            
            st.success(f"✅ Successfully generated {successful_requests}/{total_requests} isochrones!")
        else:
            st.error("❌ Failed to generate any isochrones. Please check your ORS configuration and try again.")
    
    # Display results if they exist in session state
    if st.session_state.isochrone_results is not None:
        st.divider()
        
        # Extract data from session state
        all_features = st.session_state.isochrone_results["features"]
        locations = st.session_state.isochrone_locations
        params = st.session_state.isochrone_params
        
        # Display statistics
        st.subheader(f"📊 Generated {len(all_features)} isochrone(s)")
        
        # Create summary table
        iso_data = []
        for feature in all_features:
            props = feature["properties"]
            range_value = props.get('value', 0)
            
            # Format range display
            if params["range_type"] == "time":
                range_display = f"{range_value//60} minutes"
            else:
                range_display = f"{range_value/1000:.1f} km"
            
            iso_data.append({
                "Range": range_display,
                "Area": f"{props.get('area', 0):.2f} {params['area_units']}²",
                "Center": f"({props.get('center', [0, 0])[1]:.4f}, {props.get('center', [0, 0])[0]:.4f})"
            })
        
        # Sort by range value for better display
        iso_data = sorted(iso_data, key=lambda x: float(x["Range"].split()[0]))
        df_iso = pd.DataFrame(iso_data)
        st.dataframe(df_iso, use_container_width=True, hide_index=True)
        
        # Visualization
        st.subheader("🗺️ Isochrone Visualization")
        
        if locations:
            center_lat = sum(loc[1] for loc in locations) / len(locations)
            center_lon = sum(loc[0] for loc in locations) / len(locations)
            
            iso_map = create_map([center_lat, center_lon])
            
            # Add source markers
            iso_map = add_markers_to_map(iso_map, locations, [f"Source {i+1}" for i in range(len(locations))])
            
            # Add isochrone polygons
            colors = ['red', 'orange', 'yellow', 'green', 'blue']
            
            # Sort features by range value for consistent coloring
            sorted_features = sorted(all_features, key=lambda f: f["properties"].get('value', 0))
            
            for idx, feature in enumerate(sorted_features):
                if feature["geometry"]["type"] == "Polygon":
                    coordinates = feature["geometry"]["coordinates"][0]
                    # Convert to lat,lon for folium
                    polygon_coords = [[coord[1], coord[0]] for coord in coordinates]
                    
                    range_value = feature["properties"].get('value', 0)
                    if params["range_type"] == "time":
                        popup_text = f"Reachable in {range_value//60} minutes"
                    else:
                        popup_text = f"Reachable within {range_value/1000:.1f} km"
                    
                    folium.Polygon(
                        polygon_coords,
                        color=colors[idx % len(colors)],
                        weight=2,
                        opacity=0.8,
                        fillColor=colors[idx % len(colors)],
                        fillOpacity=0.2,
                        popup=popup_text
                    ).add_to(iso_map)
            
            # Use unique key for the results map to prevent conflicts
            st_folium(iso_map, width=700, height=500, key="results_map")
        
        with st.expander("📄 Full API Response"):
            st.json(st.session_state.isochrone_results)         

# elif service == "Optimization":
#     st.header("🚛 Optimization API")
#     st.markdown("Solve vehicle routing problems (VRP) and traveling salesman problems (TSP)")
    
#     optimization_type = st.selectbox("Problem Type", ["Traveling Salesman Problem (TSP)", "Vehicle Routing Problem (VRP)"])
    
#     if optimization_type == "Traveling Salesman Problem (TSP)":
#         st.subheader("🧭 Traveling Salesman Problem")
#         st.info("Find the optimal route visiting all locations exactly once and returning to start")
        
#         col1, col2 = st.columns([1, 1])
        
#         with col1:
#             st.subheader("TSP Configuration")
#             profile = st.selectbox("Vehicle Profile", PROFILES, index=0, key="tsp_profile")
            
#             # Initialize session state for TSP locations
#             if 'tsp_locations' not in st.session_state:
#                 st.session_state.tsp_locations = [
#                     [13.404954, 52.520008],  # Berlin center
#                     [13.424954, 52.530008],  # Northeast
#                     [13.414954, 52.540008],  # North  
#                     [13.434954, 52.510008],  # Southeast
#                     [13.394954, 52.525008],  # West
#                 ]
            
#             st.subheader("📍 Locations to Visit")
            
#             # Location management
#             col_add, col_remove, col_reset = st.columns(3)
#             with col_add:
#                 if st.button("➕ Add Location"):
#                     last_loc = st.session_state.tsp_locations[-1]
#                     new_loc = [last_loc[0] + 0.01, last_loc[1] + 0.01]
#                     st.session_state.tsp_locations.append(new_loc)
#                     st.experimental_rerun()
            
#             with col_remove:
#                 if st.button("➖ Remove Last") and len(st.session_state.tsp_locations) > 3:
#                     st.session_state.tsp_locations.pop()
#                     st.experimental_rerun()
            
#             with col_reset:
#                 if st.button("🔄 Reset"):
#                     st.session_state.tsp_locations = [
#                         [13.404954, 52.520008],
#                         [13.424954, 52.530008],
#                         [13.414954, 52.540008],
#                         [13.434954, 52.510008],
#                     ]
#                     st.experimental_rerun()
            
#             # Edit locations
#             for i, loc in enumerate(st.session_state.tsp_locations):
#                 with st.expander(f"Location {i+1}", expanded=False):
#                     col_lon, col_lat = st.columns(2)
#                     with col_lon:
#                         new_lon = st.number_input(
#                             f"Longitude", 
#                             value=loc[0], 
#                             key=f"tsp_lon_{i}",
#                             format="%.6f"
#                         )
#                     with col_lat:
#                         new_lat = st.number_input(
#                             f"Latitude", 
#                             value=loc[1], 
#                             key=f"tsp_lat_{i}",
#                             format="%.6f"
#                         )
#                     st.session_state.tsp_locations[i] = [new_lon, new_lat]
            
#             st.write(f"**Total locations:** {len(st.session_state.tsp_locations)}")
        
#         with col2:
#             st.subheader("🗺️ Problem Visualization")
#             if st.session_state.tsp_locations:
#                 center_lat = sum(loc[1] for loc in st.session_state.tsp_locations) / len(st.session_state.tsp_locations)
#                 center_lon = sum(loc[0] for loc in st.session_state.tsp_locations) / len(st.session_state.tsp_locations)
                
#                 m = create_map([center_lat, center_lon])
                
#                 # Add markers with special colors
#                 for i, loc in enumerate(st.session_state.tsp_locations):
#                     color = 'red' if i == 0 else 'blue'  # Start location in red
#                     icon_symbol = 'home' if i == 0 else 'info-sign'
                    
#                     folium.Marker(
#                         [loc[1], loc[0]], 
#                         popup=f"{'START/END' if i == 0 else f'Stop {i}'}",
#                         icon=folium.Icon(color=color, icon=icon_symbol)
#                     ).add_to(m)
                
#                 st_folium(m, width=500, height=450)
        
#         if st.button("🔧 Optimize TSP Route", type="primary"):
#             # Create optimization request
#             jobs = []
#             for i in range(1, len(st.session_state.tsp_locations)):  # Skip first location (depot)
#                 jobs.append({
#                     "id": i-1,
#                     "location": st.session_state.tsp_locations[i]
#                 })
            
#             vehicles = [{
#                 "id": 0,
#                 "start": st.session_state.tsp_locations[0],  # Start at first location
#                 "end": st.session_state.tsp_locations[0],    # Return to start
#                 "profile": profile
#             }]
            
#             request_body = {
#                 "jobs": jobs,
#                 "vehicles": vehicles
#             }
            
#             with st.spinner("Optimizing TSP route..."):
#                 result, error = make_request("optimization", data=request_body, method="POST")
            
#             if result:
#                 st.success("✅ TSP route optimized!")
                
#                 # Display optimization results
#                 if "routes" in result and result["routes"]:
#                     route = result["routes"][0]
#                     steps = route["steps"]
                    
#                     st.subheader("📊 Optimization Results")
                    
#                     # Summary metrics
#                     col_dist, col_time, col_stops = st.columns(3)
#                     with col_dist:
#                         st.metric("Total Distance", f"{route.get('distance', 0)/1000:.2f} km")
#                     with col_time:
#                         duration = route.get('duration', 0)
#                         hours = duration // 3600
#                         minutes = (duration % 3600) // 60
#                         time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
#                         st.metric("Total Duration", time_str)
#                     with col_stops:
#                         job_count = len([s for s in steps if s.get('type') == 'job'])
#                         st.metric("Stops Visited", f"{job_count}/{len(jobs)}")
                    
#                     # Visit sequence
#                     st.subheader("📋 Optimized Visit Sequence")
#                     route_data = []
#                     current_time = 0
                    
#                     route_data.append({
#                         "Order": 1,
#                         "Location": "START (Depot)",
#                         "Coordinates": f"({st.session_state.tsp_locations[0][1]:.4f}, {st.session_state.tsp_locations[0][0]:.4f})",
#                         "Arrival Time": "00:00",
#                         "Type": "Depot"
#                     })
                    
#                     order = 2
#                     for step in steps:
#                         if step.get("type") == "job":
#                             job_id = step.get("job", 0)
#                             location_idx = job_id + 1  # Add 1 because job IDs start from 0 but location indices start from 1
                            
#                             arrival_time = step.get('arrival', 0)
#                             hours = arrival_time // 3600
#                             minutes = (arrival_time % 3600) // 60
#                             time_str = f"{hours:02d}:{minutes:02d}"
                            
#                             if location_idx < len(st.session_state.tsp_locations):
#                                 location = st.session_state.tsp_locations[location_idx]
#                                 route_data.append({
#                                     "Order": order,
#                                     "Location": f"Stop {job_id + 1}",
#                                     "Coordinates": f"({location[1]:.4f}, {location[0]:.4f})",
#                                     "Arrival Time": time_str,
#                                     "Type": "Customer"
#                                 })
#                                 order += 1
                    
#                     # Add return to depot
#                     route_data.append({
#                         "Order": order,
#                         "Location": "RETURN (Depot)",
#                         "Coordinates": f"({st.session_state.tsp_locations[0][1]:.4f}, {st.session_state.tsp_locations[0][0]:.4f})",
#                         "Arrival Time": f"{route.get('duration', 0)//3600:02d}:{(route.get('duration', 0)%3600)//60:02d}",
#                         "Type": "Depot"
#                     })
                    
#                     df_route = pd.DataFrame(route_data)
#                     st.dataframe(df_route, use_container_width=True, hide_index=True)
                    
#                     # Route visualization
#                     st.subheader("🗺️ Optimized Route Map")
#                     route_map = create_map([center_lat, center_lon])
                    
#                     # Add all locations with order numbers
#                     for i, loc in enumerate(st.session_state.tsp_locations):
#                         color = 'red' if i == 0 else 'green'
#                         icon = 'home' if i == 0 else 'info-sign'
                        
#                         folium.Marker(
#                             [loc[1], loc[0]], 
#                             popup=f"{'START/END' if i == 0 else f'Stop {i}'}",
#                             icon=folium.Icon(color=color, icon=icon)
#                         ).add_to(route_map)
                    
#                     # Draw optimized route if geometry is available
#                     if "geometry" in route:
#                         route_map = add_route_to_map(route_map, route["geometry"])
                    
#                     st_folium(route_map, width=700, height=500)
                
#                 with st.expander("📄 Full API Response"):
#                     st.json(result)
#             else:
#                 st.error(f"❌ Error: {error}")
    
#     else:  # Vehicle Routing Problem
#         st.subheader("🚚 Vehicle Routing Problem")
#         st.info("Optimize multiple vehicles serving multiple jobs with capacity and time constraints")
        
#         col1, col2 = st.columns([1, 1])
        
#         with col1:
#             st.subheader("🚛 Vehicle Configuration")
#             num_vehicles = st.number_input("Number of vehicles", min_value=1, max_value=5, value=2)
            
#             vehicles = []
#             for i in range(num_vehicles):
#                 with st.expander(f"Vehicle {i+1}", expanded=i == 0):
#                     col_v1, col_v2 = st.columns(2)
#                     with col_v1:
#                         v_start_lat = st.number_input(f"Start Latitude", value=52.520008 + i*0.001, key=f"v_start_lat_{i}", format="%.6f")
#                         v_start_lon = st.number_input(f"Start Longitude", value=13.404954 + i*0.001, key=f"v_start_lon_{i}", format="%.6f")
#                     with col_v2:
#                         v_end_lat = st.number_input(f"End Latitude", value=52.520008 + i*0.001, key=f"v_end_lat_{i}", format="%.6f")
#                         v_end_lon = st.number_input(f"End Longitude", value=13.404954 + i*0.001, key=f"v_end_lon_{i}", format="%.6f")
                    
#                     profile = st.selectbox(f"Profile", PROFILES, key=f"v_profile_{i}", index=0)
#                     capacity = st.number_input(f"Capacity", value=100, min_value=1, key=f"v_capacity_{i}")
                    
#                     # Time window
#                     col_t1, col_t2 = st.columns(2)
#                     with col_t1:
#                         start_time = st.time_input(f"Start time", value=datetime.strptime("08:00", "%H:%M").time(), key=f"v_start_time_{i}")
#                     with col_t2:
#                         end_time = st.time_input(f"End time", value=datetime.strptime("18:00", "%H:%M").time(), key=f"v_end_time_{i}")
                    
#                     # Convert time to seconds from midnight
#                     start_seconds = start_time.hour * 3600 + start_time.minute * 60
#                     end_seconds = end_time.hour * 3600 + end_time.minute * 60
                    
#                     vehicles.append({
#                         "id": i,
#                         "start": [v_start_lon, v_start_lat],
#                         "end": [v_end_lon, v_end_lat],
#                         "profile": profile,
#                         "capacity": [capacity],
#                         "time_window": [start_seconds, end_seconds]
#                     })
            
#             st.subheader("📦 Job Configuration")
#             num_jobs = st.number_input("Number of jobs", min_value=1, max_value=20, value=6)
            
#             jobs = []
#             for i in range(num_jobs):
#                 with st.expander(f"Job {i+1}", expanded=i < 3):
#                     col_j1, col_j2 = st.columns(2)
#                     with col_j1:
#                         j_lat = st.number_input(f"Latitude", value=52.520008 + (i*0.01), key=f"j_lat_{i}", format="%.6f")
#                         j_lon = st.number_input(f"Longitude", value=13.404954 + (i*0.01), key=f"j_lon_{i}", format="%.6f")
#                     with col_j2:
#                         j_demand = st.number_input(f"Demand", value=10, min_value=1, max_value=50, key=f"j_demand_{i}")
#                         j_service = st.number_input(f"Service time (min)", value=15, min_value=0, max_value=120, key=f"j_service_{i}")
                    
#                     # Priority and time windows
#                     j_priority = st.selectbox(f"Priority", [1, 2, 3, 4, 5], index=2, key=f"j_priority_{i}")
                    
#                     # Optional time window
#                     enable_time_window = st.checkbox(f"Enable time window", key=f"j_time_window_{i}")
                    
#                     job_data = {
#                         "id": i,
#                         "location": [j_lon, j_lat],
#                         "amount": [j_demand],
#                         "service": j_service * 60,  # Convert to seconds
#                         "priority": j_priority
#                     }
                    
#                     if enable_time_window:
#                         col_tw1, col_tw2 = st.columns(2)
#                         with col_tw1:
#                             earliest = st.time_input(f"Earliest arrival", value=datetime.strptime("09:00", "%H:%M").time(), key=f"j_earliest_{i}")
#                         with col_tw2:
#                             latest = st.time_input(f"Latest arrival", value=datetime.strptime("17:00", "%H:%M").time(), key=f"j_latest_{i}")
                        
#                         earliest_seconds = earliest.hour * 3600 + earliest.minute * 60
#                         latest_seconds = latest.hour * 3600 + latest.minute * 60
#                         job_data["time_windows"] = [[earliest_seconds, latest_seconds]]
                    
#                     jobs.append(job_data)
        
#         with col2:
#             st.subheader("🗺️ Problem Visualization")
            
#             # Create map with vehicles and jobs
#             all_points = []
#             all_labels = []
#             all_colors = []
            
#             # Add vehicle starts and ends
#             for i, vehicle in enumerate(vehicles):
#                 all_points.append(vehicle["start"])
#                 all_labels.append(f"Vehicle {i+1} Start")
#                 all_colors.append("green")
                
#                 # Only add end if different from start
#                 if vehicle["start"] != vehicle["end"]:
#                     all_points.append(vehicle["end"])
#                     all_labels.append(f"Vehicle {i+1} End")
#                     all_colors.append("darkgreen")
            
#             # Add jobs
#             for i, job in enumerate(jobs):
#                 all_points.append(job["location"])
#                 all_labels.append(f"Job {i+1} (Demand: {job['amount'][0]})")
#                 all_colors.append("red")
            
#             if all_points:
#                 center_lat = sum(p[1] for p in all_points) / len(all_points)
#                 center_lon = sum(p[0] for p in all_points) / len(all_points)
                
#                 m = create_map([center_lat, center_lon])
#                 m = add_markers_to_map(m, all_points, all_labels, all_colors)
#                 st_folium(m, width=500, height=450)
        
#         if st.button("🚛 Optimize Vehicle Routes", type="primary"):
#             request_body = {
#                 "jobs": jobs,
#                 "vehicles": vehicles
#             }
            
#             with st.spinner("Optimizing vehicle routes..."):
#                 result, error = make_request("optimization", data=request_body, method="POST")
            
#             if result:
#                 st.success("✅ Vehicle routes optimized!")
                
#                 # Display results for each vehicle
#                 if "routes" in result:
#                     st.subheader("📊 Optimization Summary")
                    
#                     # Overall summary
#                     total_distance = sum(route.get("distance", 0) for route in result["routes"]) / 1000
#                     total_duration = sum(route.get("duration", 0) for route in result["routes"]) / 3600
#                     total_jobs_assigned = sum(len([s for s in route.get("steps", []) if s.get("type") == "job"]) for route in result["routes"])
                    
#                     col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
#                     with col_sum1:
#                         st.metric("Total Distance", f"{total_distance:.2f} km")
#                     with col_sum2:
#                         st.metric("Total Duration", f"{total_duration:.1f} hours")
#                     with col_sum3:
#                         st.metric("Jobs Assigned", f"{total_jobs_assigned}/{len(jobs)}")
#                     with col_sum4:
#                         st.metric("Vehicles Used", f"{len([r for r in result['routes'] if r.get('steps')])}/{len(vehicles)}")
                    
#                     # Individual vehicle routes
#                     st.subheader("🚛 Individual Vehicle Routes")
                    
#                     for i, route in enumerate(result["routes"]):
#                         if route.get("steps"):  # Only show vehicles with assigned routes
#                             with st.expander(f"Vehicle {i+1} Route", expanded=True):
#                                 col_v1, col_v2, col_v3 = st.columns(3)
#                                 with col_v1:
#                                     st.metric("Distance", f"{route.get('distance', 0)/1000:.2f} km")
#                                 with col_v2:
#                                     st.metric("Duration", f"{route.get('duration', 0)/3600:.1f} hours")
#                                 with col_v3:
#                                     job_count = len([s for s in route.get("steps", []) if s.get("type") == "job"])
#                                     st.metric("Jobs Served", job_count)
                                
#                                 # Route details
#                                 steps = route.get("steps", [])
#                                 if steps:
#                                     route_details = []
                                    
#                                     for j, step in enumerate(steps):
#                                         step_type = step.get("type", "unknown")
#                                         arrival_time = step.get("arrival", 0)
#                                         departure_time = step.get("departure", arrival_time)
                                        
#                                         # Convert seconds to HH:MM format
#                                         arrival_str = f"{arrival_time//3600:02d}:{(arrival_time%3600)//60:02d}"
#                                         departure_str = f"{departure_time//3600:02d}:{(departure_time%3600)//60:02d}"
                                        
#                                         if step_type == "start":
#                                             description = f"Start from depot"
#                                             location = vehicles[i]["start"]
#                                         elif step_type == "job":
#                                             job_id = step.get("job", 0)
#                                             description = f"Job {job_id + 1}"
#                                             location = jobs[job_id]["location"] if job_id < len(jobs) else [0, 0]
#                                         elif step_type == "end":
#                                             description = f"Return to depot"
#                                             location = vehicles[i]["end"]
#                                         else:
#                                             description = f"Step {j+1}"
#                                             location = [0, 0]
                                        
#                                         route_details.append({
#                                             "Stop": j + 1,
#                                             "Description": description,
#                                             "Arrival": arrival_str,
#                                             "Departure": departure_str,
#                                             "Location": f"({location[1]:.4f}, {location[0]:.4f})"
#                                         })
                                    
#                                     df_vehicle_route = pd.DataFrame(route_details)
#                                     st.dataframe(df_vehicle_route, use_container_width=True, hide_index=True)
                    
#                     # Unassigned jobs
#                     if "unassigned" in result and result["unassigned"]:
#                         st.subheader("⚠️ Unassigned Jobs")
#                         unassigned_data = []
#                         for unassigned in result["unassigned"]:
#                             job_id = unassigned.get("id", 0)
#                             reason = unassigned.get("reason", "Unknown reason")
                            
#                             unassigned_data.append({
#                                 "Job ID": job_id + 1,
#                                 "Location": f"({jobs[job_id]['location'][1]:.4f}, {jobs[job_id]['location'][0]:.4f})" if job_id < len(jobs) else "N/A",
#                                 "Demand": jobs[job_id]['amount'][0] if job_id < len(jobs) else "N/A",
#                                 "Reason": reason
#                             })
                        
#                         df_unassigned = pd.DataFrame(unassigned_data)
#                         st.dataframe(df_unassigned, use_container_width=True, hide_index=True)
                        
#                         st.warning(f"💡 **Tip:** {len(result['unassigned'])} job(s) could not be assigned. Consider increasing vehicle capacity, extending time windows, or adding more vehicles.")
                    
#                     # Route visualization
#                     st.subheader("🗺️ Optimized Routes Map")
#                     route_map = create_map([center_lat, center_lon])
                    
#                     # Add vehicle depots
#                     for i, vehicle in enumerate(vehicles):
#                         folium.Marker(
#                             [vehicle["start"][1], vehicle["start"][0]], 
#                             popup=f"Vehicle {i+1} Depot",
#                             icon=folium.Icon(color='green', icon='home')
#                         ).add_to(route_map)
                    
#                     # Add jobs with different colors based on assignment
#                     assigned_jobs = set()
#                     for route in result["routes"]:
#                         for step in route.get("steps", []):
#                             if step.get("type") == "job":
#                                 assigned_jobs.add(step.get("job"))
                    
#                     for i, job in enumerate(jobs):
#                         color = 'blue' if i in assigned_jobs else 'red'
#                         icon = 'ok' if i in assigned_jobs else 'remove'
#                         status = 'Assigned' if i in assigned_jobs else 'Unassigned'
                        
#                         folium.Marker(
#                             [job["location"][1], job["location"][0]], 
#                             popup=f"Job {i+1} - {status}",
#                             icon=folium.Icon(color=color, icon=icon)
#                         ).add_to(route_map)
                    
#                     # Add route lines for each vehicle
#                     route_colors = ['blue', 'red', 'green', 'purple', 'orange']
#                     for i, route in enumerate(result["routes"]):
#                         if "geometry" in route:
#                             route_map = add_route_to_map(route_map, route["geometry"])
                    
#                     st_folium(route_map, width=700, height=500)
                
#                 with st.expander("📄 Full API Response"):
#                     st.json(result)
#             else:
#                 st.error(f"❌ Error: {error}")

elif service == "Optimization":
    st.header("🚛 Optimization API")
    st.markdown("Solve vehicle routing problems (VRP) and traveling salesman problems (TSP)")
    
    # Initialize session state for persistent results
    if 'optimization_results' not in st.session_state:
        st.session_state.optimization_results = None
    if 'optimization_type' not in st.session_state:
        st.session_state.optimization_type = "Traveling Salesman Problem (TSP)"
    if 'optimization_params' not in st.session_state:
        st.session_state.optimization_params = {}
    
    optimization_type = st.selectbox("Problem Type", ["Traveling Salesman Problem (TSP)", "Vehicle Routing Problem (VRP)"])
    
    if optimization_type == "Traveling Salesman Problem (TSP)":
        st.subheader("🧭 Traveling Salesman Problem")
        st.info("Find the optimal route visiting all locations exactly once and returning to start")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("TSP Configuration")
            profile = st.selectbox("Vehicle Profile", PROFILES, index=0, key="tsp_profile")
            
            # Initialize session state for TSP locations (Jakarta area)
            if 'tsp_locations' not in st.session_state:
                st.session_state.tsp_locations = [
                    [106.8006, -6.2446],  # Blok M area (depot)
                    [106.7932, -6.2409],  # Kolam Renang Bulungan area
                    [106.8100, -6.2350],  # Senayan area
                    [106.8200, -6.2100],  # Sudirman area
                    [106.7800, -6.2500],  # Kebayoran area
                ]
            
            st.subheader("📍 Locations to Visit")
            
            # Location management
            col_add, col_remove, col_reset = st.columns(3)
            with col_add:
                if st.button("➕ Add Location", key="tsp_add"):
                    last_loc = st.session_state.tsp_locations[-1]
                    new_loc = [last_loc[0] + 0.01, last_loc[1] + 0.01]
                    st.session_state.tsp_locations.append(new_loc)
                    st.rerun()
            
            with col_remove:
                if st.button("➖ Remove Last", key="tsp_remove") and len(st.session_state.tsp_locations) > 3:
                    st.session_state.tsp_locations.pop()
                    st.rerun()
            
            with col_reset:
                if st.button("🔄 Reset", key="tsp_reset"):
                    st.session_state.tsp_locations = [
                        [106.8006, -6.2446],  # Blok M area
                        [106.7932, -6.2409],  # Kolam Renang Bulungan
                        [106.8100, -6.2350],  # Senayan area
                        [106.8200, -6.2100],  # Sudirman area
                    ]
                    st.rerun()
            
            # Edit locations
            for i, loc in enumerate(st.session_state.tsp_locations):
                with st.expander(f"Location {i+1}", expanded=False):
                    col_lon, col_lat = st.columns(2)
                    with col_lon:
                        new_lon = st.number_input(
                            f"Longitude", 
                            value=loc[0], 
                            key=f"tsp_lon_{i}",
                            format="%.6f"
                        )
                    with col_lat:
                        new_lat = st.number_input(
                            f"Latitude", 
                            value=loc[1], 
                            key=f"tsp_lat_{i}",
                            format="%.6f"
                        )
                    st.session_state.tsp_locations[i] = [new_lon, new_lat]
            
            st.write(f"**Total locations:** {len(st.session_state.tsp_locations)}")
        
        with col2:
            st.subheader("🗺️ Problem Visualization")
            if st.session_state.tsp_locations:
                center_lat = sum(loc[1] for loc in st.session_state.tsp_locations) / len(st.session_state.tsp_locations)
                center_lon = sum(loc[0] for loc in st.session_state.tsp_locations) / len(st.session_state.tsp_locations)
                
                m = create_map([center_lat, center_lon])
                
                # Add markers with special colors
                for i, loc in enumerate(st.session_state.tsp_locations):
                    color = 'red' if i == 0 else 'blue'  # Start location in red
                    icon_symbol = 'home' if i == 0 else 'info-sign'
                    
                    folium.Marker(
                        [loc[1], loc[0]], 
                        popup=f"{'START/END' if i == 0 else f'Stop {i}'}",
                        icon=folium.Icon(color=color, icon=icon_symbol)
                    ).add_to(m)
                
                st_folium(m, width=500, height=450, key="tsp_preview_map")
        
        # Separate container for buttons
        st.divider()
        
        col_btn, col_clear = st.columns([1, 4])
        with col_btn:
            optimize_tsp_clicked = st.button("🔧 Optimize TSP Route", type="primary", key="optimize_tsp")
        with col_clear:
            if st.button("🗑️ Clear Results", key="clear_tsp"):
                st.session_state.optimization_results = None
                st.session_state.optimization_params = {}
                st.rerun()
        
        # Process optimization only when button is clicked
        if optimize_tsp_clicked:
            # Create optimization request
            jobs = []
            for i in range(1, len(st.session_state.tsp_locations)):  # Skip first location (depot)
                jobs.append({
                    "id": i-1,
                    "location": st.session_state.tsp_locations[i]
                })
            
            vehicles = [{
                "id": 0,
                "start": st.session_state.tsp_locations[0],  # Start at first location
                "end": st.session_state.tsp_locations[0],    # Return to start
                "profile": profile
            }]
            
            request_body = {
                "jobs": jobs,
                "vehicles": vehicles
            }
            
            with st.spinner("Optimizing TSP route..."):
                result, error = make_request("optimization", data=request_body, method="POST")
            
            if result:
                # Store results in session state
                st.session_state.optimization_results = result
                st.session_state.optimization_type = optimization_type
                st.session_state.optimization_params = {
                    "profile": profile,
                    "locations": st.session_state.tsp_locations.copy()
                }
                st.success("✅ TSP route optimized!")
            else:
                st.error(f"❌ Error: {error}")
    
    else:  # Vehicle Routing Problem
        st.subheader("🚚 Vehicle Routing Problem")
        st.info("Optimize multiple vehicles serving multiple jobs with capacity and time constraints")
        
        # Initialize session state for VRP
        if 'vrp_vehicles' not in st.session_state:
            st.session_state.vrp_vehicles = [
                {
                    "start": [106.8006, -6.2446],  # Blok M depot
                    "end": [106.8006, -6.2446],
                    "capacity": 100
                },
                {
                    "start": [106.8100, -6.2350],  # Senayan depot
                    "end": [106.8100, -6.2350], 
                    "capacity": 80
                }
            ]
        
        if 'vrp_jobs' not in st.session_state:
            st.session_state.vrp_jobs = [
                {"location": [106.7932, -6.2409], "demand": 15},  # Kolam Renang Bulungan
                {"location": [106.8200, -6.2100], "demand": 20},  # Sudirman area
                {"location": [106.7800, -6.2500], "demand": 10},  # Kebayoran area
                {"location": [106.8150, -6.2200], "demand": 25},  # Central Jakarta
                {"location": [106.7950, -6.2300], "demand": 12},  # Near Blok M
                {"location": [106.8050, -6.2400], "demand": 18},  # South Jakarta
            ]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🚛 Vehicle Configuration")
            num_vehicles = st.number_input("Number of vehicles", min_value=1, max_value=5, value=len(st.session_state.vrp_vehicles))
            
            # Adjust vehicles list based on number input
            while len(st.session_state.vrp_vehicles) < num_vehicles:
                st.session_state.vrp_vehicles.append({
                    "start": [106.8006, -6.2446],
                    "end": [106.8006, -6.2446],
                    "capacity": 100
                })
            while len(st.session_state.vrp_vehicles) > num_vehicles:
                st.session_state.vrp_vehicles.pop()
            
            vehicles = []
            for i in range(num_vehicles):
                with st.expander(f"Vehicle {i+1}", expanded=i == 0):
                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        v_start_lat = st.number_input(f"Start Latitude", value=st.session_state.vrp_vehicles[i]["start"][1], key=f"v_start_lat_{i}", format="%.6f")
                        v_start_lon = st.number_input(f"Start Longitude", value=st.session_state.vrp_vehicles[i]["start"][0], key=f"v_start_lon_{i}", format="%.6f")
                    with col_v2:
                        v_end_lat = st.number_input(f"End Latitude", value=st.session_state.vrp_vehicles[i]["end"][1], key=f"v_end_lat_{i}", format="%.6f")
                        v_end_lon = st.number_input(f"End Longitude", value=st.session_state.vrp_vehicles[i]["end"][0], key=f"v_end_lon_{i}", format="%.6f")
                    
                    profile = st.selectbox(f"Profile", PROFILES, key=f"v_profile_{i}", index=0)
                    capacity = st.number_input(f"Capacity", value=st.session_state.vrp_vehicles[i]["capacity"], min_value=1, key=f"v_capacity_{i}")
                    
                    # Time window
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        start_time = st.time_input(f"Start time", value=datetime.strptime("08:00", "%H:%M").time(), key=f"v_start_time_{i}")
                    with col_t2:
                        end_time = st.time_input(f"End time", value=datetime.strptime("18:00", "%H:%M").time(), key=f"v_end_time_{i}")
                    
                    # Convert time to seconds from midnight
                    start_seconds = start_time.hour * 3600 + start_time.minute * 60
                    end_seconds = end_time.hour * 3600 + end_time.minute * 60
                    
                    # Update session state
                    st.session_state.vrp_vehicles[i] = {
                        "start": [v_start_lon, v_start_lat],
                        "end": [v_end_lon, v_end_lat],
                        "capacity": capacity
                    }
                    
                    vehicles.append({
                        "id": i,
                        "start": [v_start_lon, v_start_lat],
                        "end": [v_end_lon, v_end_lat],
                        "profile": profile,
                        "capacity": [capacity],
                        "time_window": [start_seconds, end_seconds]
                    })
            
            st.subheader("📦 Job Configuration")
            num_jobs = st.number_input("Number of jobs", min_value=1, max_value=20, value=len(st.session_state.vrp_jobs))
            
            # Adjust jobs list based on number input
            while len(st.session_state.vrp_jobs) < num_jobs:
                st.session_state.vrp_jobs.append({
                    "location": [106.8006, -6.2446],
                    "demand": 10
                })
            while len(st.session_state.vrp_jobs) > num_jobs:
                st.session_state.vrp_jobs.pop()
            
            jobs = []
            for i in range(num_jobs):
                with st.expander(f"Job {i+1}", expanded=i < 3):
                    col_j1, col_j2 = st.columns(2)
                    with col_j1:
                        j_lat = st.number_input(f"Latitude", value=st.session_state.vrp_jobs[i]["location"][1], key=f"j_lat_{i}", format="%.6f")
                        j_lon = st.number_input(f"Longitude", value=st.session_state.vrp_jobs[i]["location"][0], key=f"j_lon_{i}", format="%.6f")
                    with col_j2:
                        j_demand = st.number_input(f"Demand", value=st.session_state.vrp_jobs[i]["demand"], min_value=1, max_value=50, key=f"j_demand_{i}")
                        j_service = st.number_input(f"Service time (min)", value=15, min_value=0, max_value=120, key=f"j_service_{i}")
                    
                    # Priority and time windows
                    j_priority = st.selectbox(f"Priority", [1, 2, 3, 4, 5], index=2, key=f"j_priority_{i}")
                    
                    # Optional time window
                    enable_time_window = st.checkbox(f"Enable time window", key=f"j_time_window_{i}")
                    
                    # Update session state
                    st.session_state.vrp_jobs[i] = {
                        "location": [j_lon, j_lat],
                        "demand": j_demand
                    }
                    
                    job_data = {
                        "id": i,
                        "location": [j_lon, j_lat],
                        "amount": [j_demand],
                        "service": j_service * 60,  # Convert to seconds
                        "priority": j_priority
                    }
                    
                    if enable_time_window:
                        col_tw1, col_tw2 = st.columns(2)
                        with col_tw1:
                            earliest = st.time_input(f"Earliest arrival", value=datetime.strptime("09:00", "%H:%M").time(), key=f"j_earliest_{i}")
                        with col_tw2:
                            latest = st.time_input(f"Latest arrival", value=datetime.strptime("17:00", "%H:%M").time(), key=f"j_latest_{i}")
                        
                        earliest_seconds = earliest.hour * 3600 + earliest.minute * 60
                        latest_seconds = latest.hour * 3600 + latest.minute * 60
                        job_data["time_windows"] = [[earliest_seconds, latest_seconds]]
                    
                    jobs.append(job_data)
        
        with col2:
            st.subheader("🗺️ Problem Visualization")
            
            # Create map with vehicles and jobs
            all_points = []
            all_labels = []
            all_colors = []
            
            # Add vehicle starts and ends
            for i, vehicle in enumerate(vehicles):
                all_points.append(vehicle["start"])
                all_labels.append(f"Vehicle {i+1} Start")
                all_colors.append("green")
                
                # Only add end if different from start
                if vehicle["start"] != vehicle["end"]:
                    all_points.append(vehicle["end"])
                    all_labels.append(f"Vehicle {i+1} End")
                    all_colors.append("darkgreen")
            
            # Add jobs
            for i, job in enumerate(jobs):
                all_points.append(job["location"])
                all_labels.append(f"Job {i+1} (Demand: {job['amount'][0]})")
                all_colors.append("red")
            
            if all_points:
                center_lat = sum(p[1] for p in all_points) / len(all_points)
                center_lon = sum(p[0] for p in all_points) / len(all_points)
                
                m = create_map([center_lat, center_lon])
                m = add_markers_to_map(m, all_points, all_labels, all_colors)
                st_folium(m, width=500, height=450, key="vrp_preview_map")
        
        # Separate container for buttons
        st.divider()
        
        col_btn, col_clear = st.columns([1, 4])
        with col_btn:
            optimize_vrp_clicked = st.button("🚛 Optimize Vehicle Routes", type="primary", key="optimize_vrp")
        with col_clear:
            if st.button("🗑️ Clear Results", key="clear_vrp"):
                st.session_state.optimization_results = None
                st.session_state.optimization_params = {}
                st.rerun()
        
        # Process optimization only when button is clicked
        if optimize_vrp_clicked:
            request_body = {
                "jobs": jobs,
                "vehicles": vehicles
            }
            
            with st.spinner("Optimizing vehicle routes..."):
                result, error = make_request("optimization", data=request_body, method="POST")
            
            if result:
                # Store results in session state
                st.session_state.optimization_results = result
                st.session_state.optimization_type = optimization_type
                st.session_state.optimization_params = {
                    "vehicles": vehicles,
                    "jobs": jobs
                }
                st.success("✅ Vehicle routes optimized!")
            else:
                st.error(f"❌ Error: {error}")
    
    # Display results if they exist in session state
    if st.session_state.optimization_results is not None:
        st.divider()
        
        result = st.session_state.optimization_results
        opt_type = st.session_state.optimization_type
        params = st.session_state.optimization_params
        
        if opt_type == "Traveling Salesman Problem (TSP)":
            # Display TSP results
            if "routes" in result and result["routes"]:
                route = result["routes"][0]
                steps = route["steps"]
                
                st.subheader("📊 TSP Optimization Results")
                
                # Summary metrics
                col_dist, col_time, col_stops = st.columns(3)
                with col_dist:
                    st.metric("Total Distance", f"{route.get('distance', 0)/1000:.2f} km")
                with col_time:
                    duration = route.get('duration', 0)
                    hours = duration // 3600
                    minutes = (duration % 3600) // 60
                    time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                    st.metric("Total Duration", time_str)
                with col_stops:
                    job_count = len([s for s in steps if s.get('type') == 'job'])
                    st.metric("Stops Visited", f"{job_count}/{len(params['locations'])-1}")
                
                # Visit sequence
                st.subheader("📋 Optimized Visit Sequence")
                route_data = []
                locations = params['locations']
                
                route_data.append({
                    "Order": 1,
                    "Location": "START (Depot)",
                    "Coordinates": f"({locations[0][1]:.4f}, {locations[0][0]:.4f})",
                    "Arrival Time": "00:00",
                    "Type": "Depot"
                })
                
                order = 2
                for step in steps:
                    if step.get("type") == "job":
                        job_id = step.get("job", 0)
                        location_idx = job_id + 1  # Add 1 because job IDs start from 0 but location indices start from 1
                        
                        arrival_time = step.get('arrival', 0)
                        hours = arrival_time // 3600
                        minutes = (arrival_time % 3600) // 60
                        time_str = f"{hours:02d}:{minutes:02d}"
                        
                        if location_idx < len(locations):
                            location = locations[location_idx]
                            route_data.append({
                                "Order": order,
                                "Location": f"Stop {job_id + 1}",
                                "Coordinates": f"({location[1]:.4f}, {location[0]:.4f})",
                                "Arrival Time": time_str,
                                "Type": "Customer"
                            })
                            order += 1
                
                # Add return to depot
                route_data.append({
                    "Order": order,
                    "Location": "RETURN (Depot)",
                    "Coordinates": f"({locations[0][1]:.4f}, {locations[0][0]:.4f})",
                    "Arrival Time": f"{route.get('duration', 0)//3600:02d}:{(route.get('duration', 0)%3600)//60:02d}",
                    "Type": "Depot"
                })
                
                df_route = pd.DataFrame(route_data)
                st.dataframe(df_route, use_container_width=True, hide_index=True)
                
                # Route visualization
                st.subheader("🗺️ Optimized Route Map")
                locations = params['locations']
                center_lat = sum(loc[1] for loc in locations) / len(locations)
                center_lon = sum(loc[0] for loc in locations) / len(locations)
                route_map = create_map([center_lat, center_lon])
                
                # Add all locations with order numbers
                for i, loc in enumerate(locations):
                    color = 'red' if i == 0 else 'green'
                    icon = 'home' if i == 0 else 'info-sign'
                    
                    folium.Marker(
                        [loc[1], loc[0]], 
                        popup=f"{'START/END' if i == 0 else f'Stop {i}'}",
                        icon=folium.Icon(color=color, icon=icon)
                    ).add_to(route_map)
                
                # Draw optimized route if geometry is available
                if "geometry" in route:
                    try:
                        if isinstance(route["geometry"], str):
                            # Handle encoded polyline
                            try:
                                import polyline
                                decoded_coords = polyline.decode(route["geometry"])
                                folium.PolyLine(
                                    locations=decoded_coords,
                                    color='blue',
                                    weight=4,
                                    opacity=0.8,
                                    popup="Optimized Route"
                                ).add_to(route_map)
                            except ImportError:
                                st.warning("⚠️ Install polyline library to display route: pip install polyline")
                        else:
                            # Handle other geometry formats
                            pass
                    except Exception as e:
                        st.warning(f"⚠️ Could not display route line: {str(e)}")
                
                st_folium(route_map, width=700, height=500, key="tsp_result_map")
        
        else:  # VRP Results
            if "routes" in result:
                st.subheader("📊 VRP Optimization Summary")
                
                # Overall summary
                total_distance = sum(route.get("distance", 0) for route in result["routes"]) / 1000
                total_duration = sum(route.get("duration", 0) for route in result["routes"]) / 3600
                total_jobs_assigned = sum(len([s for s in route.get("steps", []) if s.get("type") == "job"]) for route in result["routes"])
                
                col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
                with col_sum1:
                    st.metric("Total Distance", f"{total_distance:.2f} km")
                with col_sum2:
                    st.metric("Total Duration", f"{total_duration:.1f} hours")
                with col_sum3:
                    st.metric("Jobs Assigned", f"{total_jobs_assigned}/{len(params['jobs'])}")
                with col_sum4:
                    st.metric("Vehicles Used", f"{len([r for r in result['routes'] if r.get('steps')])}/{len(params['vehicles'])}")
                
                # Individual vehicle routes
                st.subheader("🚛 Individual Vehicle Routes")
                
                for i, route in enumerate(result["routes"]):
                    if route.get("steps"):  # Only show vehicles with assigned routes
                        with st.expander(f"Vehicle {i+1} Route", expanded=i == 0):
                            col_v1, col_v2, col_v3 = st.columns(3)
                            with col_v1:
                                st.metric("Distance", f"{route.get('distance', 0)/1000:.2f} km")
                            with col_v2:
                                st.metric("Duration", f"{route.get('duration', 0)/3600:.1f} hours")
                            with col_v3:
                                job_count = len([s for s in route.get("steps", []) if s.get("type") == "job"])
                                st.metric("Jobs Served", job_count)
                            
                            # Route details
                            steps = route.get("steps", [])
                            if steps:
                                route_details = []
                                vehicles = params['vehicles']
                                jobs = params['jobs']
                                
                                for j, step in enumerate(steps):
                                    step_type = step.get("type", "unknown")
                                    arrival_time = step.get("arrival", 0)
                                    departure_time = step.get("departure", arrival_time)
                                    
                                    # Convert seconds to HH:MM format
                                    arrival_str = f"{arrival_time//3600:02d}:{(arrival_time%3600)//60:02d}"
                                    departure_str = f"{departure_time//3600:02d}:{(departure_time%3600)//60:02d}"
                                    
                                    if step_type == "start":
                                        description = f"Start from depot"
                                        location = vehicles[i]["start"]
                                    elif step_type == "job":
                                        job_id = step.get("job", 0)
                                        description = f"Job {job_id + 1}"
                                        location = jobs[job_id]["location"] if job_id < len(jobs) else [0, 0]
                                    elif step_type == "end":
                                        description = f"Return to depot"
                                        location = vehicles[i]["end"]
                                    else:
                                        description = f"Step {j+1}"
                                        location = [0, 0]
                                    
                                    route_details.append({
                                        "Stop": j + 1,
                                        "Description": description,
                                        "Arrival": arrival_str,
                                        "Departure": departure_str,
                                        "Location": f"({location[1]:.4f}, {location[0]:.4f})"
                                    })
                                
                                df_vehicle_route = pd.DataFrame(route_details)
                                st.dataframe(df_vehicle_route, use_container_width=True, hide_index=True)
                
                # Route visualization
                st.subheader("🗺️ Optimized Routes Map")
                vehicles = params['vehicles']
                jobs = params['jobs']
                
                # Calculate center
                all_locs = [v["start"] for v in vehicles] + [j["location"] for j in jobs]
                center_lat = sum(loc[1] for loc in all_locs) / len(all_locs)
                center_lon = sum(loc[0] for loc in all_locs) / len(all_locs)
                
                route_map = create_map([center_lat, center_lon])
                
                # Add vehicle depots
                for i, vehicle in enumerate(vehicles):
                    folium.Marker(
                        [vehicle["start"][1], vehicle["start"][0]], 
                        popup=f"Vehicle {i+1} Depot",
                        icon=folium.Icon(color='green', icon='home')
                    ).add_to(route_map)
                
                # Add jobs with different colors based on assignment
                assigned_jobs = set()
                for route in result["routes"]:
                    for step in route.get("steps", []):
                        if step.get("type") == "job":
                            assigned_jobs.add(step.get("job"))
                
                for i, job in enumerate(jobs):
                    color = 'blue' if i in assigned_jobs else 'red'
                    icon = 'ok' if i in assigned_jobs else 'remove'
                    status = 'Assigned' if i in assigned_jobs else 'Unassigned'
                    
                    folium.Marker(
                        [job["location"][1], job["location"][0]], 
                        popup=f"Job {i+1} - {status}",
                        icon=folium.Icon(color=color, icon=icon)
                    ).add_to(route_map)
                
                st_folium(route_map, width=700, height=500, key="vrp_result_map")
        
        # Show full response in expander
        with st.expander("📄 Full API Response"):
            st.json(result)

# Footer
st.markdown("---")
st.markdown("**OpenRouteService Streamlit Interface** | Routing • Isochrones • Optimization")
st.markdown("🐳 For local ORS Docker instances | 📖 [ORS Documentation](https://openrouteservice.org/dev/)")

# Sidebar - API Status and Help
with st.sidebar:
    st.markdown("---")
    st.subheader("🔧 API Status")
    
    if st.button("Check API Health", key="sidebar_health"):
        with st.spinner("Checking..."):
            health_data, error = make_request("health")
            if health_data:
                st.success("✅ API Online")
                if "status" in health_data:
                    st.write(f"Status: {health_data['status']}")
                if "engine" in health_data:
                    engine_info = health_data["engine"]
                    st.write(f"Build Date: {engine_info.get('build_date', 'N/A')}")
                    st.write(f"Graph Date: {engine_info.get('graph_date', 'N/A')}")
            else:
                st.error("❌ API Offline")
                st.caption(f"Error: {error}")
    
    st.markdown("---")
    st.subheader("📖 Quick Reference")
    
    with st.expander("🚗 Transportation Profiles"):
        st.markdown("""
        **Driving:**
        - `driving-car` - Standard car
        - `driving-hgv` - Heavy goods vehicle
        
        **Cycling:**
        - `cycling-regular` - Regular bicycle
        - `cycling-road` - Road bike
        - `cycling-mountain` - Mountain bike
        - `cycling-electric` - E-bike
        
        **Walking:**
        - `foot-walking` - Walking
        - `foot-hiking` - Hiking trails
        - `wheelchair` - Wheelchair accessible
        """)
    
    with st.expander("🌐 API Endpoints"):
        st.markdown("""
        **Directions:**
        - `POST /directions/{profile}`
        
        **Isochrones:**
        - `POST /isochrones/{profile}`
        
        **Optimization:**
        - `POST /optimization`
        
        **Health:**
        - `GET /health`
        """)
    
    with st.expander("💡 Usage Tips"):
        st.markdown("""
        **Directions:**
        - Use 2-50 waypoints
        - Enable instructions for navigation
        - Try alternative routes
        
        **Isochrones:**
        - Max 5 locations
        - Time: up to 60 minutes
        - Distance: up to 50 km
        
        **Optimization:**
        - TSP: 3+ locations
        - VRP: Consider capacity constraints
        - Set realistic time windows
        """)

# CSS for better styling
st.markdown("""
<style>
    .stApp {
        max-width: 1400px;
        margin: 0 auto;
    }
    .stButton > button {
        width: 100%;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin: 5px 0;
    }
    .success-box {
        padding: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-box {
        padding: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)