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

# CSS PARA IMÁGENES DE PRODUCTOS Y LOGOS ALINEADOS
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
    .logo-container { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        height: 80px; 
        padding: 10px; 
    }
    .logo-container img { 
        max-height: 100%; 
        max-width: 100%; 
        object-fit: contain; 
    }
    </style>
    """, unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []

# --- FUNCIONES DE INTEGRACIÓN ---

def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 80})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
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
        remitente = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_RECEIVER"]
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = remitente, destinatario, f"🚀 NUEVO SUSCRIPTOR: {nombre}"
        cuerpo = f"Nuevo productor registrado:\n👤 {nombre}\n📧 {email_cliente}\n📞 {tel}"
        msg.attach(MIMEText(cuerpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# --- INTERFAZ ---

# 2. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in sorted(os.listdir(".")):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

todos_los_prods = get_odoo_prods()

# 3. SECCIÓN: DIAGNÓSTICO (Título corregido)
st.markdown("### 🔍 Diagnóstico Experto")
img = None
tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with tab_gal: img_gal = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam: img_cam = st.camera_input("Tomar foto")

if img_cam: img = img_cam
elif img_gal: img = img_gal

if img is not None:
    if st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
        with st.spinner("IA analizando patología y catálogo..."):
            try:
                nombres_inventario = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                # PROMPT POTENCIADO PARA PRECISIÓN Y MATCH DE PRODUCTOS
                prompt = f"""
                RESPONDE 100% EN ESPAÑOL.
                Eres un Fitopatólogo y Agrónomo Senior de Grupo Multiagro.
                1. IDENTIFICA con seguridad absoluta la plaga, hongo o deficiencia. No seas ambiguo.
                2. De esta lista de Odoo: {nombres_inventario}, elige los 4 mejores productos.
                3. Escribe los nombres de los productos recomendados en NEGRITAS (ej: **Nombre**).
                4. Justifica tu elección y da un plan de acción cultural y químico.
                """
                
                res = model.generate_content([prompt, Image.open(img)])
                texto_ia = res.text
                
                # FILTRO DE PRODUCTOS SIN REPETIR ENVASES
                texto_ia_lower = texto_ia.lower()
                sugeridos, vistos = [], set()
                if todos_los_prods:
                    for p in todos_los_prods:
                        nombre_limpio = p['name'].split('(')[0].strip().lower()
                        primera_palabra = nombre_limpio.split()[0]
                        if (nombre_limpio in texto_ia_lower or primera_palabra in texto_ia_lower) and primera_palabra not in vistos:
                            if len(primera_palabra) > 3:
                                sugeridos.append(p)
                                vistos.add(primera_palabra)
                        if len(sugeridos) >= 4: break
                
                st.session_state.chat_history = [{"role": "model", "parts": [texto_ia]}]
                st.session_state.prods_filtrados = sugeridos
                st.rerun()
            except: st.error("Error en el análisis de IA.")

if st.session_state.chat_history:
    st.markdown("---")
    st.info(st.session_state.chat_history[-1]["parts"][0])
    user_reply = st.chat_input("Escribe tu duda aquí...")
    if user_reply:
        with st.spinner("Consultando..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_reply + " (Responde siempre en español)")
            st.session_state.chat_history.append({"role": "user", "parts": [user_reply]})
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
            st.rerun()

# 4. TIENDA DINÁMICA
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            if p.get('image_128'):
                st.markdown(f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">', unsafe_allow_html=True)
            else:
                st.image("https://cdn-icons-png.flaticon.com/512/1054/1054800.png", width=150)
            st.markdown(f"**{p['name'].split('(')[0].strip()}**")
            st.write(f"RD$ {p['list_price']:,.2f}")
            link_p = f"https://wa.me/18295624653?text={urllib.parse.quote('Info sobre: ' + p['name'])}"
            st.link_button("🛒 Cotizar", link_p, use_container_width=True)

st.link_button("👨‍🌾 Hablar con un Técnico Humano", f"https://wa.me/18295624653", use_container_width=True)

# 5. REGISTRO DE PRODUCTOR (RESTABLECIDO)
st.divider()
st.markdown("### 👤 Registro de Productor")
if 'reg_ok' not in st.session_state:
    with st.form("form_registro"):
        nom = st.text_input("Nombre completo *")
        ema = st.text_input("Correo electrónico")
        tel = st.text_input("WhatsApp / Teléfono *")
        if st.form_submit_button("✅ Registrarme"):
            if nom and tel:
                if registrar_cliente_odoo(nom, ema, tel):
                    enviar_aviso_email(nom, ema, tel)
                    st.session_state['reg_ok'] = nom
                    st.rerun()
            else: st.error("Completa los campos obligatorios (*)")
else:
    st.success(f"¡Bienvenido, {st.session_state['reg_ok']}!")

# 6. LOGOS FINALES (ALINEACIÓN REFORZADA)
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#555;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
l_cols = st.columns(5)
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
for i, l in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l):
            with open(l, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{b64}"></div>', unsafe_allow_html=True)
