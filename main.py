import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import base64

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

st.markdown("""
    <style>
    .product-img {
        width: 100%;
        height: 180px;
        object-fit: contain;
        background-color: white;
        border-radius: 10px;
        padding: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state:
    st.session_state.prods_filtrados = []

# --- FUNCIONES DE INTEGRACIÓN ---
def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 40})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
            return res
    except: return None

# Cargamos el catálogo globalmente para que siempre esté disponible
todos_los_productos = get_odoo_prods()

# (Funciones de registro y email se mantienen igual...)
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

# 3. SECCIÓN: DIAGNÓSTICO
st.markdown("### 🔍 Diagnóstico e Inventario Inteligente")
img = None
tab_gal, tab_cam = st.tabs(["📁 SUBIR DE GALERÍA", "📸 USAR CÁMARA"])
with tab_gal: img_gal = st.file_uploader("Foto de la plaga", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam: img_cam = st.camera_input("Capturar")
if img_cam: img = img_cam
elif img_gal: img = img_gal

if img is not None:
    if st.button("🚀 ANALIZAR Y BUSCAR SOLUCIÓN", type="primary", use_container_width=True):
        with st.spinner("Analizando plaga y cruzando con inventario Odoo..."):
            try:
                nombres_inventario = [p['name'] for p in todos_los_productos] if todos_los_productos else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                instruccion = f"Eres Agrónomo de Multiagro. Diagnostica la imagen y de esta lista de inventario: {nombres_inventario}, elige los 4 mejores. Explica el plan de acción detallado y por qué elegiste esos productos."
                res = model.generate_content([instruccion, Image.open(img)])
                st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
                
                # Filtrar productos mencionados por la IA
                res_lower = res.text.lower()
                sugeridos = []
                if todos_los_productos:
                    for p in todos_los_productos:
                        if p['name'].split('(')[0].strip().lower() in res_lower:
                            sugeridos.append(p)
                st.session_state.prods_filtrados = sugeridos[:4]
                st.rerun()
            except: st.error("Error al procesar.")

if st.session_state.chat_history:
    st.markdown("---")
    st.info(st.session_state.chat_history[-1]["parts"][0])
    user_reply = st.chat_input("¿Dudas? Responde aquí...")
    if user_reply:
        with st.spinner("Actualizando..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_reply)
            st.session_state.chat_history.append({"role": "user", "parts": [user_reply]})
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
            st.rerun()

# 4. TIENDA (SIEMPRE VISIBLE)
st.divider()
titulo_tienda = "### 🛒 Soluciones Recomendadas para tu Problema" if st.session_state.prods_filtrados else "### 🛒 Nuestras Soluciones"
st.markdown(titulo_tienda)

# Lógica de qué mostrar: Sugeridos por IA o los primeros 4 del catálogo
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_productos[:4] if todos_los_productos else [])

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            if p.get('image_128'):
                st.markdown(f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">', unsafe_allow_html=True)
            else:
                st.image("https://cdn-icons-png.flaticon.com/512/1054/1054800.png", width=150)
            
            nombre_p = p['name'].split('(')[0].strip()
            st.markdown(f"**{nombre_p}**")
            st.write(f"RD$ {p['list_price']:,.2f}")
            link_p = f"https://wa.me/18295624653?text={urllib.parse.quote('Info sobre: ' + nombre_p)}"
            st.link_button("🛒 Cotizar", link_p, use_container_width=True)
else:
    st.info("Catálogo disponible en tienda física.")

# Botón de técnico (siempre visible)
st.link_button("👨‍🌾 Hablar con un Técnico", f"https://wa.me/18295624653", use_container_width=True)

# (Resto del código: Registro y Logos se mantienen igual...)
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
else: st.success(f"Bienvenido: {st.session_state['reg_ok']}")

st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#555;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
l_cols = st.columns(5)
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
for i, l in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l):
            img_l = Image.open(l).convert("RGBA")
            h_base = 60
            img_res = img_l.resize((int(h_base * (img_l.size[0]/img_l.size[1])), h_base), Image.Resampling.LANCZOS)
            st.image(img_res)
