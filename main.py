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

# 3. SECCIÓN: DIAGNÓSTICO DE CULTIVO (CON CHAT INTERACTIVO)
st.markdown("### 🔍 Diagnóstico de Cultivo")

img = None
tab_gal, tab_cam = st.tabs(["📁 SUBIR DE GALERÍA", "📸 USAR CÁMARA"])

with tab_gal:
    img_gal = st.file_uploader("Selecciona una foto", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam:
    st.info("Tip: Si abre la cámara frontal, usa el icono de giro en tu pantalla.")
    img_cam = st.camera_input("Capturar muestra")

if img_cam: img = img_cam
elif img_gal: img = img_gal

if img is not None:
    if st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
        with st.spinner("IA analizando..."):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                instruccion = "Eres un Agrónomo Senior de Multiagro. Analiza esta imagen, da un diagnóstico con nivel de confianza y haz 2 preguntas breves al productor para confirmar el problema."
                res = model.generate_content([instruccion, Image.open(img)])
                # Guardamos el primer resultado en el historial
                st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
            except: st.error("Error en el análisis de IA.")

# --- MOSTRAR EL RESULTADO DEL CHAT Y EL CUADRO DE RESPUESTA ---
if st.session_state.chat_history:
    st.markdown("---")
    # Mostramos el último mensaje de la IA
    st.info(st.session_state.chat_history[-1]["parts"][0])
    
    # Cuadro para que el productor responda a las preguntas de la IA
    user_reply = st.chat_input("Responde aquí a la IA (ej: 'Sí, hay puntos negros debajo')")
    
    if user_reply:
        with st.spinner("Actualizando diagnóstico..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            # Iniciamos chat con la memoria de lo hablado
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_reply)
            
            # Guardamos la conversación
            st.session_state.chat_history.append({"role": "user", "parts": [user_reply]})
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
            st.rerun()

    # Botón de Segunda Opinión Humana
    mensaje_wa = f"Hola técnico de Multiagro, necesito validar este diagnóstico:\n\n{st.session_state.chat_history[-1]['parts'][0][:200]}..."
    link_soporte = f"https://wa.me/18295624653?text={urllib.parse.quote(mensaje_wa)}"
    st.link_button("👨‍🌾 Hablar con un Técnico Humano (WhatsApp)", link_soporte, use_container_width=True)

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
