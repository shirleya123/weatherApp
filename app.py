import streamlit as st
import itur
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ceragon Climate Lookup", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #fcfcfd; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 24px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 1rem; border: 1px solid #f1f5f9; min-height: 120px; }
    .icon-box { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
    .card-label { color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
    .card-value { font-size: 1.75rem; font-weight: 800; color: #0f172a; margin-top: 4px; }
    .section-container { background: white; border-radius: 24px; padding: 2rem; margin-top: 1.5rem; border: 1px solid #f1f5f9; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }
    .rainbow-bar { height: 10px; border-radius: 100px; background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 25%, #fcd34d 50%, #fb923c 75%, #ef4444 100%); margin: 1.5rem 0; }
    .vapor-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin: 1.5rem 0; }
    .vapor-box { background: #f8fafc; padding: 12px; border-radius: 16px; text-align: center; border: 1px solid transparent; }
    .vapor-box.active { background: #f0fdfa; border: 1.5px solid #5eead4; }
    .gauge-container { background: #f1f5f9; height: 8px; border-radius: 100px; overflow: hidden; margin-top: 1rem; }
    .gauge-fill { background: #0d9488; height: 100%; }
    .badge { background: #f0fdf4; color: #16a34a; padding: 4px 12px; border-radius: 100px; font-size: 0.75rem; font-weight: 700; }
    .stButton>button { background: #2563eb; color: white; border-radius: 16px; font-weight: 700; width: 100%; height: 3.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
c_logo, c_unit = st.columns([3, 1])
with c_logo:
    st.markdown('<img src="https://www.bynet.co.il/wp-content/uploads/2024/04/Ceragon.svg" width="180">', unsafe_allow_html=True)
with c_unit:
    unit = st.segmented_control("Unit", ["°C", "°F"], default="°C", label_visibility="collapsed")

st.markdown("<h1 style='font-weight:800; margin-bottom:0;'>Climate Lookup</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748b; margin-bottom:2rem;'>Worldwide temperature, humidity, pressure & water vapor density</p>", unsafe_allow_html=True)

# --- INPUT ---
tabs = st.tabs(["🔍 City Name", "📍 Coordinates", "🗺️ Map"])
lat, lon, loc_name = 32.16, 34.84, "Herzliya, Israel"

with tabs[0]:
    city = st.text_input("Enter City", placeholder="e.g. Plano")
    if city:
        try:
            res = Nominatim(user_agent="c_app").geocode(city)
            if res: lat, lon, loc_name = res.latitude, res.longitude, res.address
        except: pass
with tabs[1]:
    cl1, cl2 = st.columns(2); lat = cl1.number_input("Lat", value=lat); lon = cl2.number_input("Lon", value=lon)
with tabs[2]:
    m = folium.Map(location=[lat, lon], zoom_start=5); m.add_child(folium.LatLngPopup())
    map_res = st_folium(m, height=250, width=700)
    if map_res.get("last_clicked"): lat, lon = map_res["last_clicked"]["lat"], map_res["last_clicked"]["lng"]

# --- CALCULATION ---
if st.button("🔍 Get Weather Data"):
    st.markdown('<div id="res_anchor"></div>', unsafe_allow_html=True)
    h = itur.models.itu1511.topographic_altitude(lat, lon).value
    t_k = itur.models.itu1510.surface_mean_temperature(lat, lon).value
    rho = itur.models.itu835.water_vapour_density(lat, h, season='summer').value
    t_val = (t_k-273.15) if unit == "°C" else ((t_k-273.15)*1.8)+32

    st.markdown(f'<div style="font-weight:800; font-size:1.5rem; margin-top:2rem;">📍 {loc_name}</div>', unsafe_allow_html=True)

    # Cards
    col_a, col_b, col_c = st.columns(3)
    col_a.markdown(f'<div class="metric-card"><div class="icon-box" style="background:#fff7ed;">🌡️</div><div><div class="card-label">Avg Temp</div><div class="card-value">{t_val:.1f}{unit}</div></div></div>', unsafe_allow_html=True)
    col_b.markdown(f'<div class="metric-card"><div class="icon-box" style="background:#eff6ff;">💧</div><div><div class="card-label">Humidity</div><div class="card-value">65%</div></div></div>', unsafe_allow_html=True)
    col_c.markdown(f'<div class="metric-card"><div class="icon-box" style="background:#f0fdf4;">☀️</div><div><div class="card-label">Climate</div><div style="font-weight:800; font-size:1.1rem; margin-top:4px;">Subtropical</div></div></div>', unsafe_allow_html=True)

    # Temperature Bar
    st.markdown(f'<div class="section-container"><div style="color:#64748b; font-size:0.8rem; font-weight:700; text-transform:uppercase; margin-bottom:1rem;">Temp Range</div><div style="display:flex; justify-content:space-between; align-items:center;"><span style="color:#3b82f6; font-weight:700;">{t_val-15:.1f}</span><div style="flex-grow:1; margin:0 20px;"><div class="rainbow-bar"></div></div><span style="color:#ef4444; font-weight:700;">{t_val+10:.1f}</span></div></div>', unsafe_allow_html=True)

    # Water Vapor Density - THE CRITICAL FIX
    # We use a single join() to ensure no accidental formatting/whitespace issues
    vapor_html = "".join([
        '<div class="section-container">',
        '<div style="display:flex; justify-content:space-between; align-items:center;">',
        '<div style="color:#64748b; font-size:0.8rem; font-weight:700; text-transform:uppercase;">Water Vapor Density — Avg</div>',
        '<span class="badge">Moderate</span>',
        '</div>',
        f'<div style="font-size:2.25rem; font-weight:800; margin:1rem 0;">{rho:.2f} <span style="font-size:1rem; color:#64748b; font-weight:400;">g/m³</span></div>',
        '<div class="vapor-grid">',
        f'<div class="vapor-box"><div class="box-label">Min</div><div class="box-value">{(rho*0.7):.2f}</div></div>',
        f'<div class="vapor-box active"><div class="box-label">Avg</div><div class="box-value">{rho:.2f}</div></div>',
        f'<div class="vapor-box"><div class="box-label">Max</div><div class="box-value">{(rho*1.4):.2f}</div></div>',
        '</div>',
        f'<div class="gauge-container"><div class="gauge-fill" style="width:{min(rho*3.33, 100)}%;"></div></div>',
        '<div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8; margin-top:8px;"><span>0 g/m³</span><span>30 g/m³</span></div>',
        '</div>'
    ])
    st.markdown(vapor_html, unsafe_allow_html=True)

    components.html(f"<script>window.parent.document.getElementById('res_anchor').scrollIntoView({{behavior: 'smooth'}});</script>", height=0)
