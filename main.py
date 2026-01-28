import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# --- CONFIGURACIÓN DE MARCA ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

# Colores Corporativos
VERDE_OSCURO = "#1B5E20"
VERDE_VIVO = "#388E3C"

# Estilos CSS Avanzados
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{
        background: white; padding: 30px; border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.03); border-top: 10px solid {VERDE_OSCURO};
    }}
    .product-card {{
        background: white; border-radius: 15px; padding: 15px;
        text-align: center; border: 1px solid #EAEAEA; transition: 0.3s;
    }}
    .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
    .footer-logos {{
        display: flex; justify-content: center; align-items: center; 
        gap: 30px; flex-wrap: wrap; padding: 30px; background: white;
        border-radius: 20px; margin-top: 50px;
    }}
    .footer-logos img {{ filter: grayscale(20%); transition: 0.3s; }}
    .footer-logos img:hover {{ filter: grayscale(0%); transform: scale(1.1); }}
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.warning("⚠️ El sistema de IA está en mantenimiento (API Key).
