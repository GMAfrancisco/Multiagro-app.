import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os, urllib.parse, time

# --- FUNCIÓN DE CONEXIÓN A ODOO ---
def traer_datos_odoo():
    try:
        url = st.secrets["ODOO_URL"]
        db = st.secrets["ODOO_DB"]
        user = st.secrets["ODOO_USER"]
        key = st.secrets["ODOO_API_KEY"]
        
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        
        if not uid: return None
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        # Buscamos productos activos en venta
        ids = models.execute_kw(db, uid, key, 'product.template', 'search', 
                               [[['sale_ok', '=', True]]], {'limit': 4})
        
        prods = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
        return [(p['name'], f"RD$ {p['list_price']:,.2f}") for p in prods]
    except:
        return None

# --- SETUP APP ---
st.set_page_config(page_title="Multiagro AgTech", layout="wide")

# IA Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except: st.error("Error IA")

# Estilos
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:20px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# Header
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico y Catálogo Odoo</h1>", unsafe_allow_html=True)

# --- BLOQUE DIAGNÓSTICO ---
st.markdown("<div class='card'>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
opc = c2.radio("Entrada:", ["Cámara", "Galería"], horizontal=True)
img = st.camera_input("Foto") if opc == "Cámara" else st.file_uploader("Subir", type=['jpg','png','jpeg'])

if img and st.button("🚀 INICIAR ANÁLISIS"):
    with st.spinner("Analizando..."):
        try:
            res = model.generate_content([f"Agrónomo RD: analiza {cult}", Image.open(img)])
            st.success("✅ Diagnóstico listo"); st.write(res.text)
        except: st.error("Límite de cuota IA alcanzado.")
st.markdown("</div>", unsafe_allow_html=True)

# --- BLOQUE ODOO ---
st.markdown("<h3 style='color:#1B5E20;margin-top:25px'>🛒 Inventario Real (Odoo)</h3>", unsafe_allow_html=True)
productos = traer_datos_odoo()

if productos:
    cols = st.columns(len(productos))
    for i, (nombre, precio) in enumerate(productos):
        with cols[i]:
            st.info(f"**{nombre}**\n\n{precio}")
            link = f"https://wa.me/18095551234?text=Interés en {nombre}"
            st.markdown(f"[💬 WhatsApp]({link})")
else:
    st.warning("No se pudo conectar con Odoo. Verifique los Secrets.")

# Logos
st.divider()
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]
l_cols = st.columns(5)
for i, l_id in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(l_id.lower()):
                im = Image.open(f)
                ratio = 80 / float(im.size[1])
                st.image(im.resize((int(im.size[0]*ratio), 80), Image.Resampling.LANCZOS))
                break

st.markdown("<p style='text-align:center;font-size:12px;color:#aaa;'>© 2026 GRUPO MULTIAGRO | Conectado a Iterativo.do</p>", unsafe_allow_html=True)
