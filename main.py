import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os

# 1. SETUP
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

# 2. ESTILOS AVANZADOS (Fuerza letras blancas en cargador y limpia logos)
st.markdown("""
    <style>
    .stApp {background-color: #F0F2F0;}
    
    /* ESTILO ÁREA DE CARGA (Drag and Drop) */
    [data-testid="stFileUploadDropzone"] {
        background-color: #333333 !important;
        border: 2px dashed #1B5E20 !important;
        border-radius: 15px;
    }
    /* Forzar letras blancas en el cargador */
    [data-testid="stFileUploadDropzone"] div div span {
        color: white !important;
    }
    [data-testid="stFileUploadDropzone"] small {
        color: #cccccc !important;
    }

    /* Tarjetas y Eslogan */
    .main-card {
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #1B5E20; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .eslogan {
        text-align: center;
        font-family: 'Georgia', serif;
        font-style: italic;
        color: #1B5E20 !important;
        font-size: 1.1rem;
        margin-top: -10px;
    }
    .product-card {
        background: white; 
        padding: 15px; 
        border-radius: 12px; 
        border: 2px solid #1B5E20; 
        text-align: center;
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

# 4. DIAGNÓSTICO
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 🔍 Diagnóstico de Cultivos")
metodo = st.radio("Seleccione método:", ["📂 Galería", "📸 Cámara"], horizontal=True)

if metodo == "📂 Galería":
    # El CSS de arriba hará que este componente tenga fondo oscuro y letras blancas
    img = st.file_uploader("Subir imagen de la planta", type=['jpg', 'jpeg', 'png'])
else:
    img = st.camera_input("Capturar muestra")

if img:
    if st.button("🚀 ANALIZAR AHORA"):
        st.info("Analizando muestra...")
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 5. PRODUCTOS ODOO
st.markdown("### 🛒 Soluciones Multiagro")
# Aquí iría tu función get_odoo_prods()
fallback = [("Fungicida Pro", "RD$ 2,500"), ("Bio-Estimulante", "RD$ 3,450")]
cols = st.columns(len(fallback))
for i, (n, p) in enumerate(fallback):
    with cols[i]:
        st.markdown(f'<div class="product-card"><b>{n}</b><br><span style="color:#1B5E20; font-weight:bold;">{p}</span></div>', unsafe_allow_html=True)
        st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text=Info:{n})")

# 6. PIE DE PÁGINA (LOGOS PNG TRANSPARENTES)
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#333;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

l_cols = st.columns(5)
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]

for i, lid in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(lid.lower()):
                # Al usar PNG transparente, el fondo blanco desaparece automáticamente
                st.image(f)
                break

st.markdown("<p style='text-align:center; font-size:12px; color:#555; margin-top:20px;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
