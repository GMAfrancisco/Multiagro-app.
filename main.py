import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

V_OSCURO = "#1B5E20"
V_VIVO = "#388E3C"

# --- IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("⚠️ Error en API Key. Verifique Secrets en Streamlit.")

# --- CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-top: 8px solid {V_OSCURO};
    }}
    .product-card {{
        background: white; border-radius: 12px; padding: 12px;
        text-align: center; border: 1px solid #EEE; min-height: 100px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA INTELIGENTE ---
def cargar_imagen_flexible(nombre_buscado, ancho=None):
    # Escanea el directorio raíz en busca del archivo
    for archivo_real in os.listdir("."):
        if archivo_real.lower() == nombre_buscado.lower():
            try:
                img = Image.open(archivo_real)
                if ancho:
                    return st.image(img, width=ancho)
                return st.image(img, use_container_width=True)
            except:
                return st.write(f"❌ Error al abrir {nombre_buscado}")
    return st.write(f"⚠️ {nombre_buscado}")

# --- HEADER ---
c_logo
