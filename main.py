import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# --- CONFIGURACIÓN DE MARCA ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

# Colores Corporativos
VERDE_OSCURO = "#1B5E20"
VERDE_VIVO = "#388E3C"

# Estilos CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{
        background: white; padding: 30px; border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.03); border-top: 10px solid {VERDE_OSCURO};
    }}
    .product-card {{
        background: white; border-radius: 15px; padding: 15px;
        text-align: center; border: 1px solid #EAEAEA;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.warning("⚠️ El sistema de IA está en mantenimiento (API Key).")

# --- CABECERA ---
st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=300)
st.markdown(f"<h1 style='color:{VERDE_OSCURO}; text-align:center;'>Asistente Inteligente Multiagro</h1>", unsafe_allow_html=True)

# --- MÓDULO DE DIAGNÓSTICO ---
with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("🔍 Diagnóstico con IA")
    
    c1, c2 = st.columns(2)
    with c1:
        cultivo = st.selectbox("Tipo de Cultivo", ["Arroz", "Banano / Plátano", "Cacao", "Vegetales Campo Abierto", "Vegetales Invernadero", "Aguacate", "Café"])
    with c2:
        modo = st.radio("Método de captura:", ["Subir Archivo", "Cámara en vivo"], horizontal=True)

    img_input = None
    if modo == "Cámara en vivo":
        img_input = st.camera_input("Capturar síntoma")
    else:
        img_input = st.file_uploader("Subir foto de la galería", type=['jpg', 'png', 'jpeg'])

    if img_input:
        st.image(img_input, width=320)
        if st.button("🚀 INICIAR DIAGNÓSTICO PROFESIONAL"):
            with st.spinner("Analizando..."):
                try:
                    img_pil = Image.open(img_input)
                    prompt = f"Como agrónomo experto
