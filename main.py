import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os, urllib.parse

# 1. SETUP
st.set_page_config(page_title="Multiagro AgTech", layout="wide")

# 2. IA (Gemini)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except: st.error("⚠️ Error: Configure GEMINI_API_KEY en Secrets.")

# 3. FUNCIÓN ODOO (Silenciosa y Segura)
def get_odoo_prods():
    try:
        url = st.secrets.get("ODOO_URL")
        db = st.secrets.get("ODOO_DB")
        user = st.secrets.get("ODOO_USER")
        key = st.secrets.get("ODOO_API_KEY")
        
        if not all([url, db, user, key]): return None
        
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', 
                                   [[['sale_ok','=',True]]], {'limit': 4})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
            return [(p['name'], f"RD$ {p['list_price']:,.2f}") for p in res]
    except: return None
    return None

# 4. UI STYLE
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:25px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 5. HEADER
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)
st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Diagnóstico Inteligente de Cultivos</h1>", unsafe_allow_html=True)

# 6. DIAGNÓSTICO IA
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opc = c2.radio("Entrada:", ["Cámara", "Galería"], horizontal=True)
    img = st.camera_input("Capturar") if opc == "Cámara" else st.file_uploader("Subir foto", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Analizando con IA fitopatológica..."):
            try:
                res = model.generate_content([f"Experto RD: analiza este {cult}, identifica plagas y sugiere manejo.", Image.open(img)])
                st.success("✅ Diagnóstico Completado")
                st.write(res.text)
            except: st.error("Límite de cuota alcanzado. Intente en unos minutos.")
    st.markdown("</div>", unsafe_allow_html=True)

# 7. PRODUCTOS (CATÁLOGO DINÁMICO)
st.markdown("<h3 style='color:#1B5E20;margin-top:30px'>🛒 Soluciones Disponibles</h3>", unsafe_allow_html=True)
odoo_prods = get_odoo_prods()

if odoo_prods:
    st.caption("🟢 Conectado a inventario real (Odoo)")
    display_prods = odoo_prods
else:
    st.caption("🟡 Catálogo promocional (Sincronización en pausa)")
    display_prods = [("Fungicida Elite", "RD$ 2,800"), ("Bio-Estimulante", "RD$ 3,450"), ("Herbicida Total", "RD$ 1,200"), ("Potasio Soluble", "RD$ 1,950")]

cols = st.columns(len(display_prods))
for i, (n, p) in enumerate(display_prods):
    with cols[i]:
        st.info(f"**{n}**\n\n{p}")
        url_wa = f"https://wa.me/18095551234?text=Interes en {n}"
        st.markdown(f"[💬 WhatsApp]({url_wa})")

# 8. LOGOS
st.divider()
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]
l_cols = st.columns(5)
for i, lid in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(lid.lower()):
                im = Image.open(f)
                ratio = 80 / float(im.size[1])
                st.image(im.resize((int(im.size[0]*ratio), 80), Image.Resampling.LANCZOS))
                break
