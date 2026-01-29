import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

# --- FUNCIONES DE INTEGRACIÓN (Odoo) ---
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
    except: return None

def registrar_cliente_odoo(nombre, email, telefono):
    try:
        url = st.secrets["ODOO_URL"]
        db = st.secrets["ODOO_DB"]
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
    except: return None

# --- FUNCIÓN PARA ENVIAR CORREO ---
def enviar_aviso_email(nombre, email_cliente, tel):
    try:
        remitente = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_RECEIVER"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"🚀 NUEVO SUSCRIPTOR: {nombre}"
        cuerpo = f"Nuevo productor interesado:\n\n👤 Nombre: {nombre}\n📧 Email: {email_cliente}\n📞 WhatsApp: {tel}"
        msg.attach(MIMEText(cuerpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# 2. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in sorted(os.listdir(".")):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# 3. DIAGNÓSTICO DE CULTIVO
st.markdown("### 🔍 Diagnóstico de Cultivo")
tab_gal, tab_cam = st.tabs(["📁 SUBIR DE GALERÍA", "📸 USAR CÁMARA"])
with tab_gal: img_gal = st.file_uploader("Foto", type=['png', 'jpg', 'jpeg'], key="gal")
with tab_cam: img_cam = st.camera_input("Capturar")
img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
    with st.spinner("Analizando..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            res = model.generate_content(["Analiza la imagen como agrónomo experto en español.", Image.open(img)])
            st.markdown(res.text)
        except: st.error("Error en IA")

# 4. SECCIÓN: SUGERENCIAS / TIENDA VIRTUAL (Odoo)
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
prods = get_odoo_prods()

if prods:
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            # 1. Limpiamos el nombre para que sea corto y profesional
            nombre_limpio = p['name'].split('(')[0].strip()
            
            # 2. Mostramos el precio destacado
            st.metric(label=nombre_limpio, value=f"RD$ {p['list_price']:,.2f}")
            
            # 3. Botón de WhatsApp real y estilizado
            texto_wa = f"Hola Grupo Multiagro, solicito cotización de: {nombre_limpio}"
            # Usamos quote para que los espacios no rompan el link
            import urllib.parse
            link_wa = f"https://wa.me/18295624653?text={urllib.parse.quote(texto_wa)}"
            
            st.link_button("💬 Cotizar por WhatsApp", link_wa, use_container_width=True)
else:
    st.warning("Cargando catálogo de productos...")

# 5. REGISTRO
st.divider()
st.markdown("### 👤 Registro de Productor")
if 'reg_ok' not in st.session_state:
    with st.form("form_reg"):
        nom = st.text_input("Nombre completo *")
        ema = st.text_input("Correo electrónico")
        tel = st.text_input("WhatsApp / Teléfono *")
        if st.form_submit_button("✅ Registrarme", use_container_width=True):
            if nom and tel:
                r_odoo = registrar_cliente_odoo(nom, ema, tel)
                enviar_aviso_email(nom, ema, tel)
                if r_odoo:
                    st.session_state['reg_ok'] = nom
                    st.rerun()
            else: st.error("Completa los campos obligatorios")
else:
    st.success(f"¡Excelente, {st.session_state['reg_ok']}! Ya estás registrado.")

# 6. LOGOS UNIFORMES
st.divider()
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
l_cols = st.columns(5)
for i, l in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l):
            img_l = Image.open(l).convert("RGBA")
            h_base = 60
            w_orig, h_orig = img_l.size
            img_res = img_l.resize((int(h_base * (w_orig/h_orig)), h_base), Image.Resampling.LANCZOS)
            st.image(img_res)
