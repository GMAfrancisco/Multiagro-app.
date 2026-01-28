import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

# 2. FUNCIONES DE INTEGRACIÓN ODOO
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

def registrar_cliente_odoo(nombre, email, telefono):
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{
                'name': nombre, 'email': email, 'phone': telefono,
                'comment': 'Registrado desde la App AgTech'
            }])
    except: return None

# 3. ESTILOS CSS (Contraste y Diseño Móvil)
st.markdown("""
    <style>
    .stApp {background-color: #F0F2F0;}
    h1, h2, h3, h4, p, label, .stMarkdown, div[data-testid="stRadio"] label {
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }
    .main-card {
        background: white; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #1B5E20; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    [data-testid="stFileUploadDropzone"] {
        background-color: #333333 !important; border: 2px dashed #1B5E20 !important; border-radius: 15px;
    }
    [data-testid="stFileUploadDropzone"] div div span { color: white !important; }
    [data-testid="stFileUploadDropzone"] small { color: #cccccc !important; }
    .product-card {
        background: #FFFFFF; padding: 15px; border-radius: 12px; 
        border: 2px solid #1B5E20; text-align: center; margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 4. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# --- BLOQUE 1: DIAGNÓSTICO ---
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 🔍 Diagnóstico de Cultivos")
metodo = st.radio("Seleccione método:", ["📂 Galería", "📸 Cámara"], horizontal=True)
img = st.file_uploader("Subir imagen de la planta", type=['png', 'jpg', 'jpeg']) if metodo == "📂 Galería" else st.camera_input("Capturar muestra")

if img and st.button("🚀 ANALIZAR AHORA"):
    with st.spinner("IA analizando..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            res = model.generate_content(["Identifica el problema y sugiere productos de Grupo Multiagro", Image.open(img)])
            st.success("✅ Diagnóstico Completado")
            st.write(res.text)
        except: st.error("Error en IA.")
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- BLOQUE 2: SOLUCIONES MULTIAGRO ---
st.markdown("### 🛒 Soluciones Multiagro")
prods = get_odoo_prods()
if prods:
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            st.markdown(f'<div class="product-card"><b>{p["name"]}</b><br><span style="color:#1B5E20; font-weight:bold;">RD$ {p["list_price"]:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f"[💬 Cotizar](https://wa.me/18295624653?text=Me%20interesa%20{p['name']})")
else: st.info("Sincronizando con inventario...")

st.divider()

# --- BLOQUE 3: REGISTRO DE PRODUCTOR (DESPUÉS DE SOLUCIONES) ---
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 👤 Registro de Productor")
if 'registro_ok' not in st.session_state:
    with st.form("form_reg"):
        n = st.text_input("Nombre Completo *")
        e = st.text_input("Correo Electrónico")
        t = st.text_input("Teléfono / WhatsApp *")
        if st.form_submit_button("✅ Registrarme"):
            if n and t:
                if registrar_cliente_odoo(n, e, t):
                    st.session_state['registro_ok'], st.session_state['user'] = True, n
                    st.rerun()
                else: st.error("Error al conectar con Odoo.")
            else: st.warning("Complete los campos obligatorios (*)")
else:
    st.success(f"¡Bienvenido, {st.session_state['user']}! Su perfil está activo.")
st.markdown("</div>", unsafe_allow_html=True)

# --- BLOQUE 4: PIE DE PÁGINA Y LOGOS ---
st.divider()
st.markdown(f"<p style='text-align:center;'>📧 info@grupomultiagro.com  |  📞 (829) 562-4653</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-weight:bold; color:#333;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

nombres_logos = [
    "LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", 
    "LogoFortius.png", "LogoAgroservicios.png"
]
l_cols = st.columns(5)

for i, nombre in enumerate(nombres_logos):
    with l_cols[i]:
        if os.path.exists(nombre):
            try:
                img_l = Image.open(nombre).convert("RGBA")
                ratio = 60 / float(img_l.size[1])
                st.image(img_l.resize((int(img_l.size[0]*ratio), 60), Image.Resampling.LANCZOS))
            except:
                st.image(nombre, width=100) # Intento de carga nativa si falla PIL
        else:
            st.caption("Cargando...")

st.markdown("<p style='text-align:center; font-size:12px; color:#555; margin-top:20px;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
