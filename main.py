import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

V_OSCURO = "#1B5E20"
V_VIVO = "#388E3C"

# --- 2. CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("⚠️ Error en API Key. Verifique Secrets.")

# --- 3. DISEÑO Y CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{ 
        background: white; padding: 25px; border-radius: 15px; 
        border-top: 8px solid {V_OSCURO}; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. CABECERA ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            try:
                img_h = Image.open(f)
                st.image(img_h, width=300)
            except:
                st.header("GRUPO MULTIAGRO")

st.markdown(f"<h1 style='text-align:center; color:{V_OSCURO};'>Consultor AgTech Multiagro</h1>", unsafe_allow_html=True)

# --- 5. DIAGNÓSTICO ---
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.subheader("🔍 Diagnóstico de Cultivos")
col_a, col_b = st.columns(2)
with col_a:
    cultivo = st.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
with col_b:
    opcion = st.radio("Entrada:", ["Subir Foto", "
