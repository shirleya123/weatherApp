import streamlit as st
import itur
import folium
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from streamlit_geolocation import streamlit_geolocation
import streamlit.components.v1 as components

# --- 1. INITIALIZE GLOBAL STATE ---
if 'lat' not in st.session_state:
    st.session_state.lat = 32.1115
if 'lon' not in st.session_state:
    st.session_state.lon = 34.9402
if 'loc_name' not in st.session_state:
    st.session_state.loc_name = "Ceragon Networks"
if 'map_center' not in st.session_state:
    st.session_state.map_center = [32.1115, 34.9402]
if 'widget_version' not in st.session_state:
    st.session_state.widget_version = 0
if 'geo_requested' not in st.session_state:
    st.session_state.geo_requested = False

# --- AUTO-LOCATION SENSOR ---
with st.sidebar:
    location = streamlit_geolocation()

if location.get('latitude') and not st.session_state.geo_requested:
    st.session_state.lat, st.session_state.lon = location['latitude'], location['longitude']
    st.session_state.map_center = [location['latitude'], location['longitude']]
    try:
        geolocator = Nominatim(user_agent="ceragon_geo_auto")
        rev = geolocator.reverse(f"{st.session_state.lat}, {st.session_state.lon}")
        st.session_state.loc_name = rev.address if rev else "Current Location"
        st.session_state.widget_version += 1
        st.session_state.geo_requested = True
        st.rerun()
    except:
        st.session_state.geo_requested = True
        st.rerun()

# --- PAGE CONFIG & CSS ---
st.set_page_config(page_title="Ceragon Climate Lookup", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #fcfcfd; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 24px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 1rem; border: 1px solid #f1f5f9; min-height: 120px; }
    .icon-box { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
    .card-label { color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
    .card-value { font-size: 1.75rem; font-weight: 800; color: #0f172a; margin-top: 4px; }
    .section-container { background: white; border-radius: 24px; padding: 2rem; margin-top: 1.5rem; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }
    .badge { background: #f0fdf4; color: #16a34a; padding: 4px 12px; border-radius: 100px; font-size: 0.75rem; font-weight: 700; }
    .stButton>button { background: #2563eb; color: white; border-radius: 16px; font-weight: 700; width: 100%; height: 3.5rem; margin-top: 20px; }
    .vapor-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin: 1.5rem 0; }
    .vapor-box { background: #f8fafc; padding: 12px; border-radius: 16px; text-align: center; border: 1px solid transparent; }
    .vapor-box.active { background: #f0fdf4; border: 1.5px solid #5eead4; }
    .box-label { font-size: 0.7rem; color: #64748b; font-weight: 600; margin-bottom: 4px; }
    .box-value { font-size: 1rem; font-weight: 700; color: #0f172a; }
    .gauge-container { background: #f1f5f9; height: 8px; border-radius: 100px; overflow: hidden; margin-top: 1rem; }
    .gauge-fill { background: #0d9488; height: 100%; }
    .chart-title { color: #64748b; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- CALLBACKS ---
geolocator = Nominatim(user_agent="ceragon_v9")

def update_from_city():
    new_city = st.session_state[f"city_box_v{st.session_state.widget_version}"]
    try:
        res = geolocator.geocode(new_city)
        if res:
            st.session_state.lat, st.session_state.lon = res.latitude, res.longitude
            st.session_state.loc_name, st.session_state.map_center = res.address, [res.latitude, res.longitude]
            st.session_state.widget_version += 1
    except: pass

def update_from_coords():
    st.session_state.lat, st.session_state.lon = st.session_state.lat_input, st.session_state.lon_input
    st.session_state.map_center = [st.session_state.lat, st.session_state.lon]
    try:
        rev = geolocator.reverse(f"{st.session_state.lat}, {st.session_state.lon}")
        st.session_state.loc_name = rev.address if rev else f"Point ({st.session_state.lat:.2f}, {st.session_state.lon:.2f})"
        st.session_state.widget_version += 1
    except: pass

# --- HEADER ---
col_logo, col_unit = st.columns([3, 1])
with col_logo:
    st.markdown('<img src="https://www.bynet.co.il/wp-content/uploads/2024/04/Ceragon.svg" width="180">', unsafe_allow_html=True)
with col_unit:
    unit = st.segmented_control("Unit", ["°C", "°F"], default="°C", label_visibility="collapsed")

st.markdown("<h1 style='font-weight:800; margin-bottom:0;'>Climate Lookup</h1>", unsafe_allow_html=True)

# --- TABS ---
tabs = st.tabs(["🔍 City Name", "📍 Coordinates", "🗺️ Map"])
with tabs[0]:
    st.text_input("Enter City", value=st.session_state.loc_name, key=f"city_box_v{st.session_state.widget_version}", on_change=update_from_city)
with tabs[1]:
    c1, c2 = st.columns(2)
    c1.number_input("Latitude", value=st.session_state.lat, format="%.4f", key="lat_input", on_change=update_from_coords)
    c2.number_input("Longitude", value=st.session_state.lon, format="%.4f", key="lon_input", on_change=update_from_coords)
with tabs[2]:
    m = folium.Map(location=st.session_state.map_center, zoom_start=6)
    folium.Marker([st.session_state.lat, st.session_state.lon]).add_to(m)
    map_data = st_folium(m, height=350, width=700, key="map_sync")
    if map_data.get("last_clicked"):
        clat, clon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        if abs(clat - st.session_state.lat) > 0.0001:
            st.session_state.lat, st.session_state.lon, st.session_state.map_center = clat, clon, [clat, clon]
            rev = geolocator.reverse(f"{clat}, {clon}")
            st.session_state.loc_name = rev.address if rev else "Map Selection"
            st.session_state.widget_version += 1
            st.rerun()

# --- THE FRAGMENT (STOPS RELOADS) ---
@st.fragment
def render_results(lat, lon, unit_type, loc_name, version):
    # Pre-calculate base ITU values
    h = itur.models.itu1511.topographic_altitude(lat, lon).value
    t_k = itur.models.itu1510.surface_mean_temperature(lat, lon).value
    rho = itur.models.itu835.water_vapour_density(lat, h, season='summer').value
    t_base = t_k - 273.15
    t_display = t_base if unit_type == "°C" else (t_base * 1.8) + 32

    st.markdown(f'<div style="font-weight:800; font-size:1.5rem; margin-top:2rem;">📍 {loc_name}</div>', unsafe_allow_html=True)

    # UI Cards
    c_a, c_b, c_c = st.columns(3)
    c_a.markdown(f'<div class="metric-card"><div class="icon-box" style="background:#fff7ed; color:#f97316;">🌡️</div><div><div class="card-label">Mean Temp</div><div class="card-value">{t_display:.1f}{unit_type}</div></div></div>', unsafe_allow_html=True)
    c_b.markdown(f'<div class="metric-card"><div class="icon-box" style="background:#eff6ff; color:#3b82f6;">💧</div><div><div class="card-label">Mean Humid</div><div class="card-value">65%</div></div></div>', unsafe_allow_html=True)
    c_c.markdown(f'<div class="metric-card"><div class="icon-box" style="background:#f0fdf4; color:#10b981;">☀️</div><div><div class="card-label">Climate</div><div style="font-weight:800; font-size:1.1rem; color:#0f172a; margin-top:4px;">Subtropical</div></div></div>', unsafe_allow_html=True)

    # Water Vapor HTML
    st.markdown(f"""
        <div class="section-container">
            <div style="color:#64748b; font-size:0.8rem; font-weight:700; text-transform:uppercase;">Water Vapor Density — Mean</div>
            <div style="font-size:2.25rem; font-weight:800; margin:1rem 0;">{rho:.2f} <span style="font-size:1rem; color:#64748b; font-weight:400;">g/m³</span></div>
            <div class="vapor-grid">
                <div class="vapor-box"><div class="box-label">Min</div><div class="box-value">{(rho * 0.7):.2f}</div></div>
                <div class="vapor-box active"><div class="box-label">Avg</div><div class="box-value">{rho:.2f}</div></div>
                <div class="vapor-box"><div class="box-label">Max</div><div class="box-value">{(rho * 1.4):.2f}</div></div>
            </div>
            <div class="gauge-container"><div class="gauge-fill" style="width:{min(rho * 3.33, 100)}%;"></div></div>
        </div>
    """, unsafe_allow_html=True)

    # --- PLOTS SECTION ---
    st.markdown("---")
    col_chart_header, col_toggle = st.columns([2, 1.2])
    with col_chart_header:
        st.markdown("### Monthly Projections")
    with col_toggle:
        # FIX: We add the version to the key to prevent DuplicateElementKey errors
        plot_range = st.segmented_control(
            "Plot Data Range:",
            ["Min", "Avg", "Max"],
            default="Avg",
            key=f"range_toggle_v{version}"
        )

    mult = 1.0 if plot_range == "Avg" else (0.75 if plot_range == "Min" else 1.25)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Render Charts
    with st.container(border=True):
        st.markdown(f'<div class="chart-title">Temperature ({unit_type}) - {plot_range}</div>', unsafe_allow_html=True)
        t_curve = (t_display * mult) + 8 * np.sin(np.linspace(-np.pi/2, 1.5*np.pi, 12))
        st.area_chart(pd.DataFrame({"Temp": t_curve}, index=months), color="#f97316", height=200)

    with st.container(border=True):
        st.markdown(f'<div class="chart-title">Humidity (%) - {plot_range}</div>', unsafe_allow_html=True)
        h_curve = (65 * mult) + 10 * np.cos(np.linspace(0, 2*np.pi, 12))
        st.bar_chart(pd.DataFrame({"Humidity": h_curve}, index=months), color="#3b82f6", height=200)

    with st.container(border=True):
        st.markdown(f'<div class="chart-title">Vapor Density (g/m³) - {plot_range}</div>', unsafe_allow_html=True)
        v_curve = (rho * mult) + (rho * 0.4) * np.sin(np.linspace(-np.pi/2, 1.5*np.pi, 12))
        st.area_chart(pd.DataFrame({"Vapor": v_curve}, index=months), color="#0d9488", height=200)

# --- EXECUTION TRIGGER ---
if st.button("🔍 Get Weather Data"):
    st.markdown('<div id="res_anchor"></div>', unsafe_allow_html=True)
    # Pass the widget_version into the fragment
    render_results(
        st.session_state.lat,
        st.session_state.lon,
        unit,
        st.session_state.loc_name,
        st.session_state.widget_version
    )
    components.html(f"<script>window.parent.document.getElementById('res_anchor').scrollIntoView({{behavior: 'smooth'}});</script>", height=0)