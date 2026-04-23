import streamlit as st
import itur
import folium
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
    st.session_state.lat = location['latitude']
    st.session_state.lon = location['longitude']
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
    .vapor-box.active { background: #f0fdfa; border: 1.5px solid #5eead4; }
    .box-label { font-size: 0.7rem; color: #64748b; font-weight: 600; margin-bottom: 4px; }
    .box-value { font-size: 1rem; font-weight: 700; color: #0f172a; }
    .gauge-container { background: #f1f5f9; height: 8px; border-radius: 100px; overflow: hidden; margin-top: 1rem; }
    .gauge-fill { background: #0d9488; height: 100%; }

    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- CALLBACKS ---
geolocator = Nominatim(user_agent="ceragon_v5_final")


def update_from_city():
    new_city = st.session_state[f"city_box_v{st.session_state.widget_version}"]
    try:
        res = geolocator.geocode(new_city)
        if res:
            st.session_state.lat, st.session_state.lon = res.latitude, res.longitude
            st.session_state.loc_name, st.session_state.map_center = res.address, [res.latitude, res.longitude]
            st.session_state.widget_version += 1
    except:
        pass


def update_from_coords():
    lat_val = st.session_state.lat_input
    lon_val = st.session_state.lon_input
    st.session_state.lat, st.session_state.lon = lat_val, lon_val
    st.session_state.map_center = [lat_val, lon_val]
    try:
        rev = geolocator.reverse(f"{lat_val}, {lon_val}")
        st.session_state.loc_name = rev.address if rev else f"Point ({lat_val:.2f}, {lon_val:.2f})"
        st.session_state.widget_version += 1
    except:
        pass


# --- HEADER ---
col_logo, col_unit = st.columns([3, 1])
with col_logo:
    st.markdown('<img src="https://www.bynet.co.il/wp-content/uploads/2024/04/Ceragon.svg" width="180">',
                unsafe_allow_html=True)
with col_unit:
    unit = st.segmented_control("Unit", ["°C", "°F"], default="°C", label_visibility="collapsed")

# --- TABS ---
tabs = st.tabs(["🔍 City Name", "📍 Coordinates", "🗺️ Map"])

with tabs[0]:
    st.text_input("Enter City", value=st.session_state.loc_name,
                  key=f"city_box_v{st.session_state.widget_version}",
                  on_change=update_from_city)

with tabs[1]:
    c1, c2 = st.columns(2)
    c1.number_input("Latitude", value=st.session_state.lat, format="%.4f", key="lat_input",
                    on_change=update_from_coords)
    c2.number_input("Longitude", value=st.session_state.lon, format="%.4f", key="lon_input",
                    on_change=update_from_coords)

with tabs[2]:
    m = folium.Map(location=st.session_state.map_center, zoom_start=6)
    folium.Marker([st.session_state.lat, st.session_state.lon]).add_to(m)
    map_data = st_folium(m, height=400, width=700, key="map_sync")
    if map_data.get("last_clicked"):
        clat, clon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        if abs(clat - st.session_state.lat) > 0.0001:
            st.session_state.lat, st.session_state.lon, st.session_state.map_center = clat, clon, [clat, clon]
            try:
                rev = geolocator.reverse(f"{clat}, {clon}")
                st.session_state.loc_name = rev.address if rev else "Map Selection"
                st.session_state.widget_version += 1
            except:
                pass
            st.rerun()

# --- CALCULATION ---
if st.button("🔍 Get Weather Data"):
    st.markdown('<div id="res_anchor"></div>', unsafe_allow_html=True)
    h = itur.models.itu1511.topographic_altitude(st.session_state.lat, st.session_state.lon).value
    t_k = itur.models.itu1510.surface_mean_temperature(st.session_state.lat, st.session_state.lon).value
    rho = itur.models.itu835.water_vapour_density(st.session_state.lat, h, season='summer').value
    t_val = (t_k - 273.15) if unit == "°C" else ((t_k - 273.15) * 1.8) + 32

    st.markdown(
        f'<div style="font-weight:800; font-size:1.5rem; margin-top:2rem;">📍 {st.session_state.loc_name}</div>',
        unsafe_allow_html=True)

    c_a, c_b, c_c = st.columns(3)
    c_a.markdown(
        f'<div class="metric-card"><div class="icon-box" style="background:#fff7ed;">🌡️</div><div><div class="card-label">Avg Temp</div><div class="card-value">{t_val:.1f}{unit}</div></div></div>',
        unsafe_allow_html=True)
    c_b.markdown(
        f'<div class="metric-card"><div class="icon-box" style="background:#eff6ff;">💧</div><div><div class="card-label">Humidity</div><div class="card-value">65%</div></div></div>',
        unsafe_allow_html=True)
    c_c.markdown(
        f'<div class="metric-card"><div class="icon-box" style="background:#f0fdf4;">☀️</div><div><div class="card-label">Climate</div><div style="font-weight:800; font-size:1.1rem; color:#0f172a; margin-top:4px;">Subtropical</div></div></div>',
        unsafe_allow_html=True)

    vapor_html = "".join([
        '<div class="section-container">',
        '<div style="display:flex; justify-content:space-between; align-items:center;">',
        '<div style="color:#64748b; font-size:0.8rem; font-weight:700; text-transform:uppercase;">Water Vapor Density — Avg</div>',
        '<span class="badge">Moderate</span>',
        '</div>',
        f'<div style="font-size:2.25rem; font-weight:800; margin:1rem 0;">{rho:.2f} <span style="font-size:1rem; color:#64748b; font-weight:400;">g/m³</span></div>',
        '<div class="vapor-grid">',
        f'<div class="vapor-box"><div class="box-label">Min</div><div class="box-value">{(rho * 0.7):.2f}</div></div>',
        f'<div class="vapor-box active"><div class="box-label">Avg</div><div class="box-value">{rho:.2f}</div></div>',
        f'<div class="vapor-box"><div class="box-label">Max</div><div class="box-value">{(rho * 1.4):.2f}</div></div>',
        '</div>',
        f'<div class="gauge-container"><div class="gauge-fill" style="width:{min(rho * 3.33, 100)}%;"></div></div>',
        '<div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8; margin-top:8px;"><span>0 g/m³</span><span>30 g/m³</span></div>',
        '</div>'
    ])
    st.markdown(vapor_html, unsafe_allow_html=True)
    components.html(
        f"<script>window.parent.document.getElementById('res_anchor').scrollIntoView({{behavior: 'smooth'}});</script>",
        height=0)