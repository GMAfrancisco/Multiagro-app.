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
            nuevo_id = models.execute_kw(db, uid, key, 'res.partner', 'create', [{
                'name': nombre,
                'email': email,
                'phone': telefono,
                'comment': 'Registrado desde la App AgTech'
            }])
            return nuevo_id
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
    .eslogan {
        text-align: center; font-family: 'Georgia', serif; font-style: italic;
        color: #1B5E20 !important; font-size: 1.1rem; margin-top: -10px; margin-bottom: 25px;
    }
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
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)
    st.markdown('<p class="eslogan">"Expertos en soluciones agrícolas"</p>', unsafe_allow_html=True)

# 5. BLOQUE 1: DIAGNÓSTICO
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 🔍 Diagnóstico de Cultivos")
metodo = st.radio("Seleccione método:", ["📂 Galería", "📸 Cámara"], horizontal=True)
img = st.file_uploader("Subir imagen de la planta", type=['jpg', 'jpeg', 'png']) if metodo == "📂 Galería" else st.camera_input("Capturar muestra")

if img and st.button("🚀 ANALIZAR AHORA"):
    with st.spinner("IA analizando..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            prompt = "Identifica el problema en la planta y sugiere soluciones de Grupo Multiagro."
            res = model.generate_content([prompt, Image.open(img)])
            st.success("✅ Diagnóstico Completado")
            st.write(res.text)
        except: st.error("Error al conectar con la IA.")
st.markdown("</div>", unsafe_allow_html=True)

# 6. BLOQUE 2: REGISTRO DE PRODUCTOR (DESPUÉS DEL DIAGNÓSTICO)
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("### 👤 Registro de Productor")
if 'registro_ok' not in st.session_state:
    st.write("Regístrese para recibir asesoría personalizada y guardar sus diagnósticos.")
    with st.form("form_registro"):
        nombre = st.text_input("Nombre Completo *")
        correo = st.text_input("Correo Electrónico")
        telefono = st.text_input("Teléfono / WhatsApp *")
        if st.form_submit_button("✅ Registrarme"):
            if nombre and telefono:
                if registrar_cliente_odoo(nombre, correo, telefono):
                    st.session_state['registro_ok'], st.session_state['user'] = True, nombre
                    st.rerun()
                else: st.error("Error al guardar en Odoo.")
            else: st.warning("Por favor llene los campos obligatorios (*)")
else:
    st.success(f"¡Bienvenido, {st.session_state['user']}! Su perfil está activo.")
st.markdown("</div>", unsafe_allow_html=True)

# 7. BLOQUE 3: SOLUCIONES MULTIAGRO
st.markdown("### 🛒 Soluciones Multiagro")
prods = get_odoo_prods()
if prods:
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            st.markdown(f'<div class="product-card"><b>{p["name"]}</b><br><span style="color:#1B5E20; font-weight:bold;">RD$ {p["list_price"]:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f"[💬 Cotizar](https://wa.me/18295624653?text=Me%20interesa%20{p['name']})")
else: st.info("Sincronizando con inventario...")

# 8. PIE DE PÁGINA (LOGOS Y CONTACTO)
st.divider()
c1, c2 = st.columns(2)
c1.markdown(f"**📧 Contacto:** info@grupomultiagro.com")
c2.markdown(f"**📞 WhatsApp:** (829) 562-4653")

st.markdown("<p style='text-align:center; font-weight:bold; margin-top:20px;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
l_cols = st.columns(5)
l_ids = ["LogoMundoAgricola", "LogoMultisemillas", "LogoMultiriegos", "LogoFortius", "LogoAgroservicios"]

for i, lid in enumerate(l_ids):
    with l_cols[i]:
        for f in os.listdir("."):
            if f.lower().startswith(lid.lower()):
                try:
                    img_logo = Image.open(f)
                    ratio = 60 / float(img_logo.size[1])
                    st.image(img_logo.resize((int(img_logo.size[0]*ratio), 60), Image.Resampling.LANCZOS))
                except: pass
                break
st.markdown("<p style='text-align:center; font-size:12px; color:#555;'>© 2026 GRUPO MULTIAGRO | República Dominicana</p>", unsafe_allow_html=True)
