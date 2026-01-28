import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import os

# --- 1. CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="Multiagro App", layout="wide")

# --- 2. CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except Exception as e:
    st.error("Error de configuración de IA")

# --- 3. DISEÑO Y CABECERA ---
st.markdown("<h1 style='text-align:center; color:#1B5E20;'>GRUPO MULTIAGRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Consultor AgTech Profesional</p>", unsafe_allow_html=True)

# Intentar cargar el logo principal solo si existe
if os.path.exists("Grupo_Multiagro_Mesa de trabajo 1.png"):
    st.image("Grupo_Multiagro_Mesa de trabajo 1.png", width=300)

# --- 4. MÓDULO DE DIAGNÓSTICO (LA PRIORIDAD) ---
st.divider()
st.subheader("🔍 Diagnóstico con IA")

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
                st.success("Análisis completado")
                st.write(res.text)
            except Exception as e:
                st.error(f"Error en el análisis: {e}")

# --- 5. PRODUCTOS ---
st.divider()
st.subheader("🛒 Catálogo")
items = [
    {"n": "Fungicida Elite", "p": "RD$ 2,800"},
    {"n": "Bio-Estimulante", "p": "RD$ 3,450"},
    {"n": "Herbicida Total", "p": "RD$ 1,200"},
    {"n": "Potasio Soluble", "p": "RD$ 1,950"}
]
p_cols = st.columns(4)
for i in range(len(items)):
    with p_cols[i]:
        st.info(f"**{items[i]['n']}**\n\n{items[i]['p']}")
        txt_wa = urllib.parse.quote(f"Interés en: {items[i]['n']}")
        st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text={txt_wa})")

# --- 6. LOGOS EMPRESAS (VERSION SIMPLIFICADA) ---
st.divider()
st.markdown("<p style='text-align:center; color:gray;'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)

logos = [
    "Logo Mundo Agricola.jpg", 
    "Logo Multisemillas.jpg", 
    "IMG-20251217-WA0012.jpg", 
    "Logo-Fortius.png", 
    "Logo-Agroservicios-Final_Mesa de trabajo 1.png"
]

l_cols = st.columns(len(logos))
for i, l_nombre in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l_nombre):
            st.image(l_nombre, use_container_width=True)
        else:
            st.caption(f"Marca {i+1}")
