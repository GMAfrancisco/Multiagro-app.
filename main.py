import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Multiagro App", page_icon="🌱", layout="wide")

# --- FUNCION MAESTRA PARA CARGAR IMAGENES ---
def cargar_logo_seguro(nombre_archivo):
    # Buscamos en el directorio actual
    for file in os.listdir("."):
        if file.lower() == nombre_archivo.lower():
            try:
                img = Image.open(file)
                return st.image(img, use_container_width=True)
            except:
                pass
    return st.caption(f"Archivo: {nombre_archivo}")

# --- HEADER ---
col_logo_main = st.columns([1, 2, 1])
with col_logo_main[1]:
    cargar_logo_seguro("Grupo_Multiagro_Mesa de trabajo 1.png")

st.markdown("<h2 style='text-align:center; color:#1B5E20;'>Consultor AgTech</h2>", unsafe_allow_html=True)

# --- (El resto de tu código de IA y Productos se mantiene igual) ---
# ... (Mantén tu lógica de diagnóstico aquí arriba) ...

# --- PIE DE PÁGINA (LOGOS MARCAS) ---
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>NUESTRAS EMPRESAS</p>", unsafe_allow_html=True)

listado_logos = [
    "Logo Mundo Agricola.jpg", 
    "Logo Multisemillas.jpg", 
    "IMG-20251217-WA0012.jpg", 
    "Logo-Fortius.png", 
    "Logo-Agroservicios-Final_Mesa de trabajo 1.png"
]

cols_logos = st.columns(len(listado_logos))
for i, l_nombre in enumerate(listado_logos):
    with cols_logos[i]:
        cargar_logo_seguro(l_nombre)
