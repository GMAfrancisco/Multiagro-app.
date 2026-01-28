import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro App", layout="wide")

# --- 2. CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("Error en API Key.")

# --- 3. ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAF8; }
    .product-card {
        background: white; padding: 20px; border-radius: 15px;
        text-align: center; border-top: 5px solid #1B5E20;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ESCÁNER DE ARCHIVOS (PARA LOS LOGOS) ---
archivos = os.listdir(".")
st.sidebar.write("### 📂 Archivos en el servidor:")
st.sidebar.write(archivos)

def mostrar_logo(nombre):
    for f in archivos:
        if f.lower() == nombre.lower():
            return st.image(f, use_container_width=True)
    return st.caption(f"❌ {nombre}")

# --- 5. CABECERA ---
st.markdown("<h1 style='text-align:center; color:#1B5E20;'>GRUPO MULTIAGRO</h1>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    mostrar_logo("Grupo_Multiagro_Mesa de trabajo 1.png")

# --- 6. DIAGNÓSTICO ---
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    cultivo = st.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
with col_b:
    opcion = st.radio("Método:", ["Subir Foto", "Usar Cámara"], horizontal=True)

img_input = None
if opcion == "Usar Cámara":
    img_input = st.camera_input("Capturar")
else:
    img_input = st.file_uploader("Galería", type=['jpg', 'png', 'jpeg'])

if img_input:
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            try:
                pil_img = Image.open(img_input)
                prompt = f"Como agrónomo en RD, analiza este {cultivo} e identifica plagas."
                res = model.generate_content([prompt, pil_img])
                st.success("Diagnóstico listo")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error: {e}")

#
