import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image, ImageFile
import os

# --- PREVENCIÓN DE ERRORES DE MEMORIA ---
Image.MAX_IMAGE_PIXELS = None 
ImageFile.LOAD_TRUNCATED_IMAGES = True

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide", initial_sidebar_state="collapsed")

# 2. FUNCIONES DE INTEGRACIÓN (Odoo)
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
                'comment': 'Cliente registrado desde App AgTech'
            }])
    except: return None

# 3. ESTILOS VISUALES
st.markdown("""
    <style>
    .stApp {background-color: #F0F2F0;}
    h1, h2, h3, h4, p, label { color: #1A1A1A !important; font-weight: 600 !important; }
    .card { background: white; padding: 20px; border-radius: 15px; border-left: 8px solid #1B5E20; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1B5E20; color: white; }
    </style>
""", unsafe_allow_html=True)

# 4. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# --- SECCIÓN 1: DIAGNÓSTICO DE IA ---
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🔍 Diagnóstico de Cultivos")
img = st.camera_input("Capturar muestra") if st.toggle("Usar Cámara") else st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'])

if img and st.button("🚀 ANALIZAR AHORA"):
    with st.spinner("Analizando con IA..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            # INSTRUCCIÓN DETALLADA EN ESPAÑOL
            instruccion = """
            Actúa como un experto agrónomo de Grupo Multiagro en República Dominicana.
            Analiza la imagen de la planta y:
            1. Identifica la posible plaga, enfermedad o deficiencia nutricional.
            2. Responde SIEMPRE en español de forma clara y profesional.
            3. Recomienda el uso de productos específicos que vende Grupo Multiagro 
               (insecticidas, herbicidas o fertilizantes según sea el caso).
            """
            
            res = model.generate_content([instruccion, Image.open(img)])
            st.success("✅ Diagnóstico Completado")
            st.info(res.text)
        except: 
            st.error("Error al procesar la imagen con la IA.")

# --- SECCIÓN 2: SOLUCIONES (ODOO) ---
st.divider()
st.subheader("🛒 Soluciones Multiagro")
prods = get_odoo_prods()
if prods:
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            st.markdown(f"**{p['name']}**")
            st.markdown(f"<span style='color:#1B5E20; font-size:1.2rem;'>RD$ {p['list_price']:,.2f}</span>", unsafe_allow_html=True)
            st.link_button("Cotizar", f"https://wa.me/18295624653?text=Info:{p['name']}")
else: st.info("Cargando catálogo...")

# --- SECCIÓN 3: REGISTRO (DESPUÉS DE SOLUCIONES) ---
st.divider()
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("👤 Registro de Productor")
if 'reg' not in st.session_state:
    with st.form("registro"):
        n, e, t = st.text_input("Nombre completo *"), st.text_input("Email"), st.text_input("WhatsApp *")
        if st.form_submit_button("✅ Guardar mi Registro"):
            if n and t:
                if registrar_cliente_odoo(n, e, t):
                    st.session_state['reg'] = n
                    st.rerun()
                else: st.error("No se pudo conectar con Odoo.")
            else: st.warning("Nombre y WhatsApp son obligatorios.")
else:
    st.success(f"¡Gracias por registrarte, {st.session_state['reg']}!")
st.markdown("</div>", unsafe_allow_html=True)

# --- SECCIÓN 4: LOGOS DE EMPRESAS ---
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
l_cols = st.columns(5)

for i, l in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l):
            try:
                # Carga segura para evitar DecompressionBomb
                st.image(l, use_container_width=True)
            except: st.caption("Empresa")
        else: st.caption("Multiagro")

st.markdown("<p style='text-align:center; font-size:0.8rem; color:gray;'>© 2026 GRUPO MULTIAGRO | info@grupomultiagro.com</p>", unsafe_allow_html=True)
