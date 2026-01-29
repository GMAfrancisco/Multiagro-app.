import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

# --- FUNCIONES ODOO ---
def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 4})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
            return res
    except: return None

# 2. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in sorted(os.listdir(".")):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# 3. SECCIÓN DE DIAGNÓSTICO (Galería primero para no abrir cámara sola)
st.markdown("### 🔍 Análisis de Cultivos")
tab_gal, tab_cam = st.tabs(["📁 SUBIR DE GALERÍA", "📸 USAR CÁMARA"])

with tab_gal:
    img_gal = st.file_uploader("Selecciona una foto", type=['png', 'jpg', 'jpeg'], key="gal")

with tab_cam:
    img_cam = st.camera_input("Capturar muestra")

img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ANÁLISIS TÉCNICO", type="primary", use_container_width=True):
    with st.spinner("IA analizando..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            instruccion = "Eres un agrónomo experto de Grupo Multiagro en RD. Analiza el problema en la imagen y da un diagnóstico profundo con técnicas de control y productos recomendados en español."
            res = model.generate_content([instruccion, Image.open(img)])
            st.markdown(res.text)
        except: st.error("Error en el análisis.")

# --- SECCIÓN 4: PIE DE PÁGINA (Logos Uniformes) ---
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#333; margin-bottom:20px;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

# Lista de archivos
logos = [
    "LogoMundoAgricola.png", 
    "LogoMultisemillas.png", 
    "LogoMultiriegos.png", 
    "LogoFortius.png", 
    "LogoAgroservicios.png"
]

# Creamos las 5 columnas
l_cols = st.columns(len(logos))

for i, nombre_archivo in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(nombre_archivo):
            try:
                # Abrimos la imagen
                img = Image.open(nombre_archivo).convert("RGBA")
                
                # NORMALIZACIÓN: Forzamos una altura de 60px para todos
                altura_deseada = 60
                ancho_original, altura_original = img.size
                ratio = ancho_original / altura_original
                nuevo_ancho = int(altura_deseada * ratio)
                
                # Redimensionamos con alta calidad
                img_resized = img.resize((nuevo_ancho, altura_deseada), Image.Resampling.LANCZOS)
                
                # Mostramos la imagen centrada
                st.image(img_resized, use_container_width=False)
            except:
                st.caption("Multiagro")
        else:
            st.caption("Falta Logo")

st.markdown("<p style='text-align:center; font-size:0.8rem; color:gray; margin-top:30px;'>© 2026 GRUPO MULTIAGRO | República Dominicana</p>", unsafe_allow_html=True)
