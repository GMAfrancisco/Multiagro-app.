import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Multiagro App", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Colores Corporativos Multiagro
V_OSCURO = "#1B5E20"
V_VIVO = "#388E3C"

# --- 2. CONFIGURACIÓN IA GEMINI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Usamos la versión 2.0 Flash Lite para mayor velocidad y menor consumo de cuota
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except Exception as e:
    st.error("⚠️ Error de configuración de IA. Verifique los Secrets en Streamlit.")

# --- 3. ESTILOS CSS PERSONALIZADOS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-top: 8px solid {V_OSCURO};
        margin-bottom: 20px;
    }}
    .product-card {{
        background: white; border-radius: 12px; padding: 15px;
        text-align: center; border: 1px solid #EEE; min-height: 120px;
        transition: transform 0.3s;
    }}
    .product-card:hover {{
        transform: translateY(-5px);
        box-shadow
