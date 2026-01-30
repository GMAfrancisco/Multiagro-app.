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

# Estilo para homogeneizar imágenes de Odoo
st.markdown("""
    <style>
    .product-img { width: 100%; height: 180px; object-fit: contain; background-color: white; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Inicializar estados de sesión
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
            # Buscamos productos con stock y venta activa
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 100})
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
            new_id = models.execute_kw(db, uid, key, 'res.partner', 'create', [{
                'name': nombre, 'email': email, 'phone': telefono,
                'comment': 'Registrado desde App AgTech Multiagro'
            }])
            return new_id
    except: return None

def enviar_aviso_email(nombre, email_cliente, tel):
    try:
        remitente = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_RECEIVER"]
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = remitente, destinatario, f"🚀 NUEVO SUSCRIPTOR: {nombre}"
        cuerpo = f"Se ha registrado un nuevo productor:\n\n👤 Nombre: {nombre}\n📧 Email: {email_cliente}\n📞 Tel: {tel}"
        msg.attach(MIMEText(cuerpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# --- INICIO DE LA APP ---

# 2. ENCABEZADO
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in sorted(os.listdir(".")):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

# Cargamos catálogo
todos_los_prods = get_odoo_prods()

# 3. SECCIÓN: DIAGNÓSTICO
st.markdown("### 🔍 Diagnóstico Fitosanitario Experto")
img = None
tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with tab_gal: img_gal = st.file_uploader("Subir imagen del cultivo", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam: img_cam = st.camera_input("Tomar foto")

if img_cam: img = img_cam
elif img_gal: img = img_gal

if img is not None:
    if st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
        with st.spinner("IA analizando plaga y catálogo..."):
            try:
                # Extraer nombres para la IA
                nombres_odoo = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                prompt = f"""
                Eres un Fitopatólogo Senior de Grupo Multiagro.
                1. IDENTIFICA la plaga/enfermedad con precisión técnica.
                2. De este catálogo: {nombres_odoo}, SELECCIONA los productos ideales.
                3. Da un plan de manejo cultural y químico detallado.
                4. Usa negritas para los productos recomendados.
                """
                
                res = model.generate_content([prompt, Image.open(img)])
                st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
                
                # Filtrar duplicados visualmente (por primera palabra del nombre)
                texto_ia = res.text.lower()
                sugeridos = []
                vistos = set()
                if todos_los_prods:
                    for p in todos_los_prods:
                        clave = p['name'].split()[0].lower()
                        if clave in texto_ia and clave not in vistos and len(clave) > 3:
                            sugeridos.append(p)
                            vistos.add(clave)
                        if len(sugeridos) >= 4: break
                st.session_state.prods_filtrados = sugeridos
                st.rerun()
            except: st.error("Error en el análisis de IA.")

if st.session_state.chat_history:
    st.markdown("---")
    st.info(st.session_state.chat_history[-1]["parts"][0])
    
    # Chat interactivo
    user_reply = st.chat_input("¿Deseas más detalles sobre el tratamiento?")
    if user_reply:
        with st.spinner("Consultando experto..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_reply)
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
            st.markdown(f"**{p['name'].split('(')[0].strip()}**")
            st.write(f"RD$ {p['list_price']:,.2f}")
            link_p = f"https://wa.me/18295624653?text={urllib.parse.quote('Info sobre: ' + p['name'])}"
            st.link_button("🛒 Cotizar", link_p, use_container_width=True)

# Botón siempre presente para hablar con un técnico
st.link_button("👨‍🌾 Hablar con un Técnico Humano", f"https://wa.me/18295624653", use_container_width=True)

# 5. REGISTRO DE PRODUCTOR
st.divider()
st.markdown("### 👤 Registro de Productor")
if 'reg_ok' not in st.session_state:
    with st.form("form_registro"):
        nom = st.text_input("Nombre completo *")
        ema = st.text_input("Correo electrónico")
        tel = st.text_input("WhatsApp / Teléfono *")
        if st.form_submit_button("✅ Registrarme y recibir asesoría"):
            if nom and tel:
                with st.spinner("Procesando..."):
                    if registrar_cliente_odoo(nom, ema, tel):
                        enviar_aviso_email(nom, ema, tel)
                        st.session_state['reg_ok'] = nom
                        st.rerun()
            else: st.error("Por favor completa los campos con (*)")
else:
    st.success(f"¡Bienvenido, {st.session_state['reg_ok']}! Ya estamos procesando tu solicitud.")

# 6. LOGOS FINALES
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:#555;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
l_cols = st.columns(5)
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
for i, l in enumerate(logos):
    with l_cols[i]:
        if os.path.exists(l): st.image(l, use_container_width=True)
