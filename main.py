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
    # Modelo 2026 optimizado
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except Exception as e:
    st.error("⚠️ Error de configuración de IA. Verifique los Secrets.")

# --- 3. ESTILOS CSS PERSONALIZADOS (Triple comilla verificada) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAF8; }}
    .main-card {{
        background: white; 
        padding: 25px; 
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
        border-top: 8px solid {V_OSCURO};
        margin-bottom: 20px;
    }}
    .product-card {{
        background: white; 
        border-radius: 12px; 
        padding: 15px;
        text-align: center; 
        border: 1px solid #EEE; 
        min-height: 140px;
        transition: transform 0.3s;
    }}
    .product-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}
    .stButton>button {{
        width: 100%; 
        background-color: {V_OSCURO}; 
        color: white;
        border-radius: 10px; 
        border: none; 
        height: 3em;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIÓN DE CARGA DE IMÁGENES (Súper Flexible) ---
def cargar_logo_final(nombre_sin_extension, ancho=None):
    if not os.path.exists("."):
        return None
    archivos_reales = os.listdir(".")
    for f in archivos_reales:
        nombre_base = os.path.splitext(f)[0].lower()
        if nombre_base == nombre_sin_extension.lower():
            try:
                img = Image.open(f)
                if ancho:
                    return st.image(img, width=ancho)
                return st.image(img, use_container_width=True)
            except:
                continue
    return st.caption(f"⚠️ {nombre_sin_extension}")

# --- 5. CABECERA Y LOGO PRINCIPAL ---
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    cargar_logo_final("Grupo_Multiagro_Mesa de trabajo 1", ancho=300)

st.markdown(f"<h1 style='text-align:center; color:{V_OSCURO};'>Asistente AgTech Profesional</h1>", unsafe_allow_html=True)

# --- 6. MÓDULO DE DIAGNÓSTICO CON IA ---
with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{V_OSCURO};'>🔍 Diagnóstico de Cultivos</h2>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        cultivo = st.selectbox("Seleccione el Cultivo:", 
            ["Arroz", "Banano / Plátano", "Cacao", "Vegetales Campo Abierto", 
             "Vegetales Invernadero", "Aguacate", "Café", "Otros"])
    with col_b:
        opcion = st.radio("Método de entrada:", ["Subir Foto", "Usar Cámara"], horizontal=True)

    img_input = None
    if opcion == "Usar Cámara":
        img_input = st.camera_input("Capturar síntoma en el campo")
    else:
        img_input = st.file_uploader("Cargar imagen desde galería", type=['jpg', 'png', 'jpeg'])

    if img_input:
        st.image(img_input, width=350, caption="Imagen para análisis")
