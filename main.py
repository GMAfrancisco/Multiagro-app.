import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

# --- FUNCIONES DE INTEGRACIÓN (Odoo) ---
def get_odoo_prods():
    try:
        url = st.secrets["ODOO_URL"]
        db = st.secrets["ODOO_DB"]
        user = st.secrets["ODOO_USER"]
        key = st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        
        if not uid:
            # Esto nos dirá en la consola de Streamlit si falló el login
            print("Error: Autenticación fallida en Odoo")
            return None
            
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        # Buscamos productos que tengan "Venta ok" y que tengan stock o sean servicios
        ids = models.execute_kw(db, uid, key, 'product.template', 'search', 
                               [[['sale_ok','=',True], ['type','!=','service']]], 
                               {'limit': 4})
        res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price']})
        return res
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def registrar_cliente_odoo(nombre, email, telefono):
    try:
        url = st.secrets["ODOO_URL"]
        db = st.secrets.get("ODOO_DB", "odoo-multiriegos-prod-12691727")
        user = st.secrets["ODOO_USER"]
        key = st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{
                'name': nombre, 'email': email, 'phone': telefono,
                'comment': 'Registrado desde App AgTech Multiagro'
            }])
    except:
        return None

# 2. ENCABEZADO (Logo Principal)
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in sorted(os.listdir(".")):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# 3. SECCIÓN: DIAGNÓSTICO DE CULTIVO
st.markdown("### 🔍 Diagnóstico de Cultivo")
tab_gal, tab_cam = st.tabs(["📁 SUBIR DE GALERÍA", "📸 USAR CÁMARA"])

with tab_gal:
    img_gal = st.file_uploader("Selecciona una foto", type=['png', 'jpg', 'jpeg'], key="gal")
with tab_cam:
    img_cam = st.camera_input("Capturar muestra")

img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
    with st.spinner("IA analizando..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            instruccion = """Eres un agrónomo experto de Grupo Multiagro en RD. Analiza el problema y da un diagnóstico profundo con técnicas de control y productos recomendados en español."""
            res = model.generate_content([instruccion, Image.open(img)])
            st.markdown(res.text)
        except:
            st.error("Error en el análisis de IA.")

# 4. SECCIÓN: SUGERENCIAS / TIENDA VIRTUAL (Odoo)
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
prods = get_odoo_prods()
if prods:
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            st.info(f"**{p['name']}**\n\nRD$ {p['list_price']:,.2f}")
            st.markdown(f"[💬 Cotizar](https://wa.me/18295624653?text=Hola, quiero info de: {p['name']})")
else:
    st.warning("Cargando catálogo de productos...")

# 5. SECCIÓN: REGISTRO DEL CLIENTE
st.divider()
st.markdown("### 👤 Registro de Productor")
if 'reg_ok' not in st.session_state:
    with st.form("form_reg"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nombre completo *")
            ema = st.text_input("Correo electrónico")
        with col2:
            tel = st.text_input("WhatsApp / Teléfono *")
        if st.form_submit_button("✅ Registrarme"):
            if nom and tel:
                if registrar_cliente_odoo(nom, ema, tel):
                    st.session_state['reg_ok'] = nom
                    st.rerun()
                else:
                    st.error("No se pudo conectar con Odoo. Revisa la base de datos.")
            else:
                st.error("Por favor completa los campos obligatorios (*)")
else:
    st.success(f"¡Excelente, {st.session_state['reg_ok']}! Ya estás registrado en nuestro sistema.")

# 6. PIE DE PÁGINA (Logos Uniformes)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#333; margin-bottom:20px;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)

logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
l_cols = st.columns(len(logos))

for i, l in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l):
            try:
                img_l = Image.open(l).convert("RGBA")
                h_base = 60 
                w_orig, h_orig = img_l.size
                w_new = int(h_base * (w_orig / h_orig))
                img_res = img_l.resize((w_new, h_base), Image.Resampling.LANCZOS)
                st.image(img_res)
            except:
                st.caption("Multiagro")
        else:
            st.caption("Empresa")

st.markdown("<p style='text-align:center; font-size:0.8rem; color:gray; margin-top:30px;'>© 2026 GRUPO MULTIAGRO</p>", unsafe_allow_html=True)
