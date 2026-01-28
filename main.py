import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os, urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Multiagro AgTech", layout="wide")

# 2. ESCÁNER AUTOMÁTICO DE ODOO
def buscar_db_correcta():
    url = st.secrets["ODOO_URL"]
    user = st.secrets["ODOO_USER"]
    key = st.secrets["ODOO_API_KEY"]
    
    # Lista de nombres que Iterativo suele asignar
    intentos = ["multiriegos_prod", "multiriegos-prod", "prod", "multiriegos", "prod_multiriegos"]
    
    for db_test in intentos:
        try:
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
            uid = common.authenticate(db_test, user, key, {})
            if uid:
                # Si conecta, trae 4 productos para probar
                models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
                ids = models.execute_kw(db_test, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 4})
                res = models.execute_kw(db_test, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
                return res, db_test
        except:
            continue
    return None, None

# 3. IA GEMINI
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except:
    st.error("⚠️ Configurar Gemini API Key en Secrets")

# 4. DISEÑO Y ESTILOS
st.markdown("<style>.stApp{background:#F8FAF8} .card{background:white;padding:25px;border-radius:15px;border-top:8px solid #1B5E20;box-shadow:0 4px 10px rgba(0,0,0,0.05)}</style>", unsafe_allow_html=True)

# 5. HEADER
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown("<h1 style='text-align:center;color:#1B5E20;margin-top:-20px;'>Consultor AgTech Multiagro</h1>", unsafe_allow_html=True)

# 6. DIAGNÓSTICO IA
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cult = c1.selectbox("Cultivo:", ["Arroz", "Banano", "Cacao", "Vegetales", "Aguacate", "Café"])
    opc = c2.radio("Entrada:", ["Cámara", "Galería"], horizontal=True)
    img = st.camera_input("Foto") if opc == "Cámara" else st.file_uploader("Subir", type=['jpg','png','jpeg'])
    
    if img and st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Analizando..."):
            try:
                res = model.generate_content([f"Agrónomo RD: analiza {cult}", Image.open(img)])
                st.success("✅ Diagnóstico Completado"); st.write(res.text)
            except: st.error("Error en IA. Verifique cuota.")
    st.markdown("</div>", unsafe_allow_html=True)

# 7. SECCIÓN DE ODOO (CATÁLOGO REAL)
st.markdown("<h3 style='color:#1B5E20;margin-top:25px'>🛒 Soluciones Disponibles (Inventario Real)</h3>", unsafe_allow_html=True)

productos, db_encontrada = buscar_db_correcta()

if productos:
    st.success(f"✅ Conectado a Odoo. Base de datos detectada: **{db_encontrada}**")
    cols = st.columns(len(productos))
    for i, p in enumerate(productos):
        with cols[i]:
            st.info(f"**{p['name']}**\n\nRD$ {p['list_price']:,.2f}")
            link = f"https://wa.me/18095551234?text=Interes en {p['name']}"
            st.markdown(f"[💬 Cotizar]({link})")
else:
    st.warning("🔄 Buscando conexión con Odoo... (Mostrando catálogo promocional)")
    fallback = [("Fungicida Elite", "RD$ 2,800"), ("Bio-Estimulante", "RD$ 3,450"), ("Herbicida Total", "RD$ 1,200"), ("Potasio Soluble", "RD$ 1,950")]
    cols = st.columns(4)
    for i, (n, p) in enumerate(fallback):
        with cols[i]:
            st.info(f"**{n}**\n\n{p}")

# 8. LOGOS GRUPO
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

st.markdown("<p style='text-align:center;font-size:12px;color:#aaa;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
