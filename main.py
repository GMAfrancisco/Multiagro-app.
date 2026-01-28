import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os

# 1. SETUP
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

# 2. ESTILOS CSS (Contraste Selectivo)
st.markdown("""
    <style>
    .stApp {background-color: #F0F2F0;}
    
    /* Títulos y etiquetas en NEGRO para legibilidad */
    h1, h2, h3, h4, p, label, .stMarkdown, .stRadio label {
        color: #1A1A1A !important;
        font-weight: 600;
    }

    /* TARJETA DE DIAGNÓSTICO */
    .main-card {
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #1B5E20; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* ÁREA DE CARGA: Fondo oscuro y letras BLANCAS (solo aquí) */
    [data-testid="stFileUploadDropzone"] {
        background-color: #333333 !important;
        border: 2px dashed #1B5E20 !important;
        border-radius: 15px;
    }
    [data-testid="stFileUploadDropzone"] div div span {
        color: white !important; /* Letras blancas dentro del cuadro */
    }
    [data-testid="stFileUploadDropzone"] small {
        color: #cccccc !important;
    }

    /* ESlogan en cursiva verde */
    .eslogan {
        text-align: center;
        font-family: 'Georgia', serif;
        font-style: italic;
        color: #1B5E20 !important;
        font-size: 1.1rem;
        margin-top: -10px;
    }

    /* Botones de radio (Galería/Cámara) en NEGRO */
    div[data-testid="stRadio"] > label {
        color: #1A1A1A !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)
    st.markdown('<p class="eslogan">"Expertos en soluciones agrícolas"</p>', unsafe_allow_html=True)

# 4. SECCIÓN DIAGNÓSTICO (Texto ahora en Negro)
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 🔍 Diagnóstico de Cultivos") # Este saldrá negro

metodo = st.radio("Seleccione método:", ["📂 Galería", "📸 Cámara"], horizontal=True)

if metodo == "📂 Galería":
    # El título "Subir imagen..." saldrá negro, el cuadro será oscuro con letras blancas
    img = st.file_uploader("Subir imagen de la planta", type=['jpg', 'jpeg', 'png'])
else:
    img = st.camera_input("Capturar muestra")

if img:
    if st.button("🚀 ANALIZAR AHORA"):
        st.info("Analizando muestra...")
st.markdown("</div>", unsafe_allow_html=True)

# 5. PRODUCTOS Y LOGOS (Siguen la misma lógica de contraste)
st.divider()
st.markdown("### 🛒 Soluciones Multiagro")
# ... resto de tu código de productos y logos ...
