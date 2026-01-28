import streamlit as st
from PIL import Image
import os

# --- SOLUCIÓN DE EMERGENCIA ---
# Forzamos a ignorar el límite de píxeles
try:
    from PIL import ImageFile
    Image.MAX_IMAGE_PIXELS = None
    ImageFile.LOAD_TRUNCATED_IMAGES = True
except:
    pass

st.set_page_config(page_title="Grupo Multiagro", layout="wide")

# 1. ESTILOS BÁSICOS
st.markdown("""
    <style>
    .stApp {background-color: #F0F2F0;}
    .main-card {
        background: white; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #1B5E20; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# 3. CUERPO (Simulado para que no falle)
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.subheader("🔍 Diagnóstico y Soluciones")
st.write("La aplicación se está reiniciando correctamente...")
st.markdown("</div>", unsafe_allow_html=True)

# 4. PIE DE PÁGINA (Logos con prueba de error)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

# Nombres exactos que vimos en tu lista
nombres_logos = [
    "LogoMundoAgricola.png", 
    "LogoMultisemillas.png", 
    "LogoMultiriegos.png", 
    "LogoFortius.png", 
    "LogoAgroservicios.png"
]

cols = st.columns(5)
for i, nombre in enumerate(nombres_logos):
    with cols[i]:
        if os.path.exists(nombre):
            try:
                # Intentamos abrirlo de la forma más ligera posible
                img = Image.open(nombre)
                st.image(img, use_container_width=True)
            except Exception as e:
                st.caption("Error de formato")
        else:
            st.caption("No encontrado")

st.markdown("<p style='text-align:center; font-size:12px; color:#555;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
