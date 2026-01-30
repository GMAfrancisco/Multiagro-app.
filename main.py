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

# --- INICIALIZACIÓN DE MEMORIA DE CHAT ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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

img = None
tab_gal, tab_cam = st.tabs(["📁 SUBIR DE GALERÍA", "📸 USAR CÁMARA"])

with tab_gal:
    img_gal = st.file_uploader("Selecciona una foto", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam:
    st.info("Tip: Asegura buena iluminación para un mejor detalle de la plaga.")
    img_cam = st.camera_input("Capturar muestra")

if img_cam: img = img_cam
elif img_gal: img = img_gal

if img is not None:
    if st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
        with st.spinner("IA realizando peritaje detallado..."):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                # INSTRUCCIÓN RE-POTENCIADA
                instruccion = """
                Eres el Agrónomo Principal de Grupo Multiagro. Realiza un diagnóstico exhaustivo:
                
                1. IDENTIFICACIÓN: Nombre común y científico de la plaga, hongo o deficiencia detectada. Explica brevemente los síntomas visibles.
                2. NIVEL DE DAÑO: Evalúa la gravedad (Leve, Moderada, Crítica).
                3. PRÁCTICAS DE CAMPO: Sugiere métodos de control cultural (poda, riego, eliminación de hospederos, etc.).
                4. RECOMENDACIÓN DE PRODUCTOS: Sugiere productos específicos disponibles en Multiagro (insecticidas, fungicidas o fertilizantes foliares) indicando el porqué de su elección.
                5. PREGUNTAS DE CIERRE: Haz 2 preguntas clave para confirmar (ej. condiciones climáticas o extensión del daño).
                
                Formato: Usa negritas para productos y secciones. Sé muy detallado pero profesional.
                """
                
                res = model.generate_content([instruccion, Image.open(img)])
                st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
            except: st.error("Error en el análisis de IA.")

if st.session_state.chat_history:
    st.markdown("---")
    st.markdown(st.session_state.chat_history[-1]["parts"][0])
    
    user_reply = st.chat_input("Responde aquí a la IA para precisar detalles...")
    
    if user_reply:
        with st.spinner("Refinando diagnóstico..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_reply)
            st.session_state.chat_history.append({"role": "user", "parts": [user_reply]})
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
            st.rerun()

    # Botón de Soporte
    nombre_productor = st.session_state.get('reg_ok', 'un productor')
    msg_wa = f"Hola técnico de Multiagro, soy {nombre_productor}. Necesito ayuda con este diagnóstico:\n\n{st.session_state.chat_history[-1]['parts'][0][:300]}..."
    link_wa = f"https://wa.me/18295624653?text={urllib.parse.quote(msg_wa)}"
    st.link_button("👨‍🌾 Validar con un Técnico Humano (WhatsApp)", link_wa, use_container_width=True)

# 4. TIENDA
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            # Agregamos 'image_128' a los campos solicitados
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 4})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
            return res
    except: return None

# 5. REGISTRO
st.divider()
st.markdown("### 👤 Registro de Productor")
if 'reg_ok' not in st.session_state:
    with st.form("form_reg"):
        n, e, t = st.text_input("Nombre *"), st.text_input("Email"), st.text_input("WhatsApp *")
        if st.form_submit_button("✅ Registrarme", use_container_width=True):
            if n and t:
                if registrar_cliente_odoo(n, e, t):
                    enviar_aviso_email(n, e, t)
                    st.session_state['reg_ok'] = n
                    st.rerun()
            else: st.error("Completa los campos obligatorios")
else:
    st.success(f"¡Sesión activa como: {st.session_state['reg_ok']}!")

# 6. LOGOS
st.divider()
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
l_cols = st.columns(5)
for i, l in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l):
            img_l = Image.open(l).convert("RGBA")
            h_base = 60
            img_res = img_l.resize((int(60 * (img_l.size[0]/img_l.size[1])), 60), Image.Resampling.LANCZOS)
            st.image(img_res)
