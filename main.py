import streamlit as st
from PIL import Image, ImageFile
import os

# CONFIGURACIÓN CRÍTICA PARA MEMORIA
Image.MAX_IMAGE_PIXELS = None 
ImageFile.LOAD_TRUNCATED_IMAGES = True

st.set_page_config(page_title="Grupo Multiagro", layout="wide")

# CSS para mantener el estilo
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

# 1. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# 2. CUERPO TEMPORAL
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.subheader("✅ Sistema Restablecido")
st.write("Si ves este mensaje, la App ya está funcionando de nuevo. Ahora podemos proceder a reactivar la IA y Odoo.")
st.markdown("</div>", unsafe_allow_html=True)

# 3. PIE DE PÁGINA (Logos)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

nombres_logos = [
    "LogoMundoAgricola.png", "LogoMultisemillas.png", 
    "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"
]

cols = st.columns(5)
for i, nombre in enumerate(nombres_logos):
    with cols[i]:
        if os.path.exists(nombre):
            try:
                # Cargamos de forma nativa para ahorrar RAM
                st.image(nombre, use_container_width=True)
            except:
                st.caption("Error de archivo")
        else:
            st.caption("No encontrado")

st.markdown("<p style='text-align:center; font-size:12px; color:#555; margin-top:20px;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
