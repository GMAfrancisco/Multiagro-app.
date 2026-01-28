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
    st.error("⚠️ Error en API Key.")

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

# --- HEADER ---
# Buscamos el logo principal ignorando mayúsculas/minúsculas
def mostrar_imagen(nombre_archivo, ancho=None):
    for file in os.listdir("."):
        if file.lower() == nombre_archivo.lower():
            return st.image(file, width=ancho) if ancho else st.image(file, use_container_width=True)
    return st.write(f"⚠️ No encontrado: {nombre_archivo}")

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
mostrar_imagen("Grupo_Multiagro_Mesa de trabajo 1.png", ancho=280)
st.markdown("</div>", unsafe_allow_html=True)

# --- DIAGNÓSTICO ---
with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{V_OSCURO};'>🔍 Diagnóstico IA</h2>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        cultivo = st.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales Campo Abierto", "Vegetales Invernadero", "Aguacate", "Café"])
    with col_b:
        opcion = st.radio("Acción:", ["Subir Foto", "Usar Cámara"], horizontal=True)

    img = None
    if opcion == "Usar Cámara":
        img = st.camera_input("Capturar")
    else:
        img = st.file_uploader("Galería", type=['jpg', 'png', 'jpeg'])

    if img:
        st.image(img, width=300)
        if st.button("🚀 ANALIZAR AHORA"):
            with st.spinner("Analizando..."):
                try:
                    pil_img = Image.open(img)
                    prompt = f"Como agrónomo en RD, analiza este {cultivo} e identifica plagas."
                    res = model.generate_content([prompt, pil_img])
                    st.success("¡Diagnóstico listo!")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PRODUCTOS ---
st.markdown("<br><h3>🛒 Catálogo</h3>", unsafe_allow_html=True)
items = [{"n": "Fungicida Elite", "p": "RD$ 2,800"}, {"n": "Bio-Estimulante", "p": "RD$ 3,450"}]
c = st.columns(2)
for i in range(len(items)):
    with c[i]:
        st.markdown(f"<div class='product-card'><b>{items[i]['n']}</b><br>{items[i]['p']}</div>", unsafe_allow_html=True)

# --- LOGOS (MARCAS ALIADAS) ---
st.markdown("---")
st.markdown("<p style='text-align:center; color:#999; font-weight:bold;'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)

logos_ficheros = [
    "Logo Mundo Agricola.jpg", 
    "Logo Multisemillas.jpg", 
    "IMG-20251217-WA0012.jpg", 
    "Logo-Fortius.png", 
    "Logo-Agroservicios-Final_Mesa de trabajo 1.png"
]

l_cols = st.columns(len(logos_ficheros))
for i, l_nombre in enumerate(logos_ficheros):
    with l_cols[i]:
        mostrar_imagen(l_nombre)

st.markdown("<p style='text-align:center; font-size:12px; color:#aaa; margin-top:50px;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
