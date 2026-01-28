import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os, urllib.parse

# 1. SETUP PROFESIONAL
st.set_page_config(page_title="Grupo Multiagro | Consultor AgTech", layout="wide")

# 2. IA Y ODOO
def get_odoo_prods():
    try:
        url = st.secrets["ODOO_URL"]
        db = st.secrets["ODOO_DB"]
        user = st.secrets["ODOO_USER"]
        key = st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 4})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
            return res
    except:
        return None

# 3. ESTILOS CSS
st.markdown("""
    <style>
    .stApp {background-color: #F4F7F4;}
    .main-card {background: white; padding: 25px; border-radius: 15px; border-top: 8px solid #1B5E20; box-shadow: 0 4px 10px rgba(0,0,0,0.05);}
    .product-card {background:white; padding:15px; border-radius:10px; border:1px solid #e0e0e0; text-align:center;}
    </style>
""", unsafe_allow_html=True)

# 4. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)

st.markdown("<h2 style='text-align:center; color:#1B5E20; margin-top:-20px;'>Asistente Técnico Inteligente</h2>", unsafe_allow_html=True)

# 5. CATÁLOGO DE PRODUCTOS
st.markdown("### 🛒 Soluciones Multiagro")
prods = get_odoo_prods()
if prods:
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            st.markdown(f"<div class='product-card'><b>{p['name']}</b><br><span style='color:#1B5E20; font-size:18px;'>RD$ {p['list_price']:,.2f}</span></div>", unsafe_allow_html=True)
            st.markdown(f"[💬 WhatsApp](https://wa.me/18095551234?text=Info:{p['name']})")
else:
    c1, c2, c3, c4 = st.columns(4)
    for col, texto in zip([c1,c2,c3,c4], ["Fungicida", "Herbicida", "Fertilizante", "Insecticida"]):
        col.info(f"**{texto}**\n\nConsulte Precio")

st.divider()

# 6. MÓDULO DE DIAGNÓSTICO
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 🔍 Diagnóstico de Cultivos")
metodo = st.radio("Seleccione método:", ["📂 Galería", "📸 Cámara"], horizontal=True)

if metodo == "📂 Galería":
    img = st.file_uploader("Subir imagen de la planta", type=['jpg', 'jpeg', 'png'])
else:
    img = st.camera_input("Capturar muestra")

if img:
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            # Aquí se activaría la lógica de Gemini
            st.success("Imagen recibida. Procesando diagnóstico...")
st.markdown("</div>", unsafe_allow_html=True)

# 7. PIE DE PÁGINA Y LOGOS
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#555;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]
l_cols = st.columns(5)

for i, lid in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(lid.lower()):
                try:
                    img_logo = Image.open(f)
                    ratio = 80 / float(img_logo.size[1])
                    new_size = (int(img_logo.size[0] * ratio), 80)
                    st.image(img_logo.resize(new_size, Image.Resampling.LANCZOS))
                except:
                    pass
                break

st.markdown("<p style='text-align:center; font-size:12px; color:#aaa; margin-top:20px;'>© 2026 GRUPO MULTIAGRO | República Dominicana</p>", unsafe_allow_html=True)
