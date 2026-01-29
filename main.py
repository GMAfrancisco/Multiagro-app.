import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

# --- FUNCIONES DE INTEGRACIÓN ---
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
                'comment': 'Registrado desde App AgTech Multiagro'
            }])
    except: return None

def enviar_aviso_email(nombre, email_cliente, tel):
    try:
        remitente, password = st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_RECEIVER"]
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = remitente, destinatario, f"🚀 NUEVO SUSCRIPTOR: {nombre}"
        cuerpo = f"Nuevo productor:\n👤 {nombre}\n📧 {email_cliente}\n📞 {tel}"
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

# 3. SECCIÓN: DIAGNÓSTICO DE CULTIVO
st.markdown("### 🔍 Diagnóstico de Cultivo")

# IMPORTANTE: Inicializamos las variables para evitar el NameError
img = None
tab_gal, tab_cam = st.tabs(["📁 SUBIR DE GALERÍA", "📸 USAR CÁMARA"])

with tab_gal:
    img_gal = st.file_uploader("Selecciona una foto", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam:
    st.info("Tip: Si abre la cámara frontal, usa el icono de giro en tu pantalla.")
    img_cam = st.camera_input("Capturar muestra")

# Asignamos la imagen a la variable global 'img'
if img_cam:
    img = img_cam
elif img_gal:
    img = img_gal

# Solo ejecutamos si 'img' no es None
if img is not None:
    st.success("✅ Imagen lista")
    if st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
        with st.spinner("IA analizando calidad y patología..."):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                instruccion = """
                Eres un Agrónomo Senior de Grupo Multiagro. 
                1. Evalúa la calidad de la imagen. 
                2. Da un diagnóstico técnico con Nivel de Confianza (%).
                3. Recomienda productos de Multiagro y técnicas de control.
                4. Haz 2 preguntas clave al productor para validar el problema.
                Responde en español dominicano profesional de forma estructurada.
                """
                
                res = model.generate_content([instruccion, Image.open(img)])
                diag_texto = res.text
                st.markdown("---")
                st.markdown(diag_texto)
                
                # Botón de Segunda Opinión Humana
                st.warning("¿Deseas validar este resultado con un experto?")
                mensaje_wa = f"Hola técnico de Multiagro, necesito validar este diagnóstico de la IA:\n\n{diag_texto[:300]}..."
                link_soporte = f"https://wa.me/18295624653?text={urllib.parse.quote(mensaje_wa)}"
                st.link_button("👨‍🌾 Contactar Servicio Técnico (WhatsApp)", link_soporte, use_container_width=True)
                
            except Exception as e:
                st.error("Error en el análisis. Intenta con otra foto.")

# 4. TIENDA (Sugerencias)
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
prods = get_odoo_prods()
if prods:
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            nombre_p = p['name'].split('(')[0].strip()
            st.metric(label=nombre_p, value=f"RD$ {p['list_price']:,.2f}")
            link_p = f"https://wa.me/18295624653?text={urllib.parse.quote('Me interesa el producto: ' + nombre_p)}"
            st.link_button("💬 Cotizar WhatsApp", link_p, use_container_width=True)

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
                if registrar_cliente_odoo(nom, ema, tel):
                    enviar_aviso_email(nom, ema, tel)
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
