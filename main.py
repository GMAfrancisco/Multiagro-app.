¡Mil disculpas! Tienes toda la razón. En el afán de limpiar el código, moví piezas que no debía. El eslogan va exactamente debajo del logo y la frase de "Diagnóstico de Cultivos" debe permanecer como encabezado de la sección de IA, ya que es la guía del usuario.

Aquí tienes la versión corregida, manteniendo el eslogan en cursiva bajo el logo y restaurando la frase de Diagnóstico en su lugar correspondiente.

🛠️ Código Corregido (Eslogan + Frase de Diagnóstico)
Python
import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os

# 1. SETUP PROFESIONAL
st.set_page_config(page_title="Grupo Multiagro | Consultor AgTech", layout="wide")

# 2. FUNCIÓN ODOO
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

# 3. ESTILOS CSS
st.markdown("""
    <style>
    .stApp {background-color: #F4F7F4;}
    .main-card {background: white; padding: 25px; border-radius: 15px; border-top: 8px solid #1B5E20; box-shadow: 0 4px 10px rgba(0,0,0,0.05);}
    .product-card {background:white; padding:15px; border-radius:10px; border:1px solid #e0e0e0; text-align:center;}
    .eslogan {
        text-align: center;
        font-family: 'Georgia', serif;
        font-style: italic;
        color: #1B5E20;
        font-size: 1rem;
        margin-top: -15px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# 4. ENCABEZADO (Logo + Eslogan justo debajo)
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)
    # ESlogan pegado al logo
    st.markdown('<p class="eslogan">"Expertos en soluciones agrícolas"</p>', unsafe_allow_html=True)

# --- BLOQUE 1: DIAGNÓSTICO (Con su frase restaurada) ---
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 🔍 Diagnóstico de Cultivos") # <-- Frase restaurada
st.write("Identifique plagas o deficiencias. La IA le sugerirá productos de nuestro catálogo.")

metodo = st.radio("Seleccione método:", ["📂 Galería", "📸 Cámara"], horizontal=True)

if metodo == "📂 Galería":
    img = st.file_uploader("Subir imagen de la planta", type=['jpg', 'jpeg', 'png'])
else:
    img = st.camera_input("Capturar muestra")

if img:
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                prompt = "Analiza esta planta, identifica el problema y sugiere productos de Soluciones Multiagro."
                res = model.generate_content([prompt, Image.open(img)])
                st.success("Análisis Técnico:")
                st.write(res.text)
            except: st.error("Error de conexión con IA.")
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- BLOQUE 2: SOLUCIONES MULTIAGRO ---
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
    for col, t in zip([c1,c2,c3,c4], ["Fungicida", "Herbicida", "Fertilizante", "Insecticida"]):
        col.info(f"**{t}**\n\nConsultar precio")

# --- BLOQUE 3: LOGOS ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#555;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
l_cols = st.columns(5)
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]

for i, lid in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(lid.lower()):
                try:
                    img_l = Image.open(f)
                    ratio = 80 / float(img_l.size[1])
                    st.image(img_l.resize((int(img_l.size[0]*ratio), 80), Image.Resampling.LANCZOS))
                except: pass
                break
