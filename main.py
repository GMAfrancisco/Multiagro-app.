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

# Estilo para imágenes homogéneas
st.markdown("""
    <style>
    .product-img { width: 100%; height: 180px; object-fit: contain; background-color: white; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state:
    st.session_state.prods_filtrados = []

# --- FUNCIONES ---
def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 50})
            res = models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
            return res
    except: return None

todos_los_productos = get_odoo_prods()

# (Funciones de registro y email omitidas para brevedad, mantener las mismas que ya tienes)
def registrar_cliente_odoo(nombre, email, telefono):
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{ 'name': nombre, 'email': email, 'phone': telefono, 'comment': 'Registrado desde App' }])
    except: return None

def enviar_aviso_email(n, e, t):
    try:
        rem, pas = st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = rem, st.secrets["EMAIL_RECEIVER"], f"🚀 Nuevo Registro: {n}"
        msg.attach(MIMEText(f"Nombre: {n}\nEmail: {e}\nTel: {t}", 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(rem, pas)
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

# 3. SECCIÓN: DIAGNÓSTICO POTENCIADO
st.markdown("### 🔍 Diagnóstico e Inventario Inteligente")
img = None
tab_gal, tab_cam = st.tabs(["📁 SUBIR DE GALERÍA", "📸 USAR CÁMARA"])
with tab_gal: img_gal = st.file_uploader("Foto de la plaga", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam: img_cam = st.camera_input("Capturar")
if img_cam: img = img_cam
elif img_gal: img = img_gal

if img is not None:
    if st.button("🚀 INICIAR PERITAJE TÉCNICO", type="primary", use_container_width=True):
        with st.spinner("IA detectando patologías..."):
            try:
                nombres_inventario = [p['name'] for p in todos_los_productos] if todos_los_productos else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                # PROMPT AGRESIVO DE DIAGNÓSTICO
                instruccion = f"""
                Eres un Patólogo Agrónomo Senior de Grupo Multiagro.
                1. ANALIZA visualmente la imagen buscando ácaros, trips, manchas de hongos (Roya, Mildiu), o deficiencias.
                2. Si la imagen no es clara, descríbela y pide una mejor foto del envés de la hoja.
                3. De esta lista de inventario: {nombres_inventario}, selecciona los 4 que combaten el problema detectado.
                4. Usa negritas para los nombres de los productos recomendados.
                5. Justifica técnicamente tu elección y da un plan de acción.
                """
                
                res = model.generate_content([instruccion, Image.open(img)])
                st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
                
                # FILTRO FLEXIBLE (Busca coincidencias parciales)
                texto_ia = res.text.lower()
                sugeridos = []
                if todos_los_productos:
                    for p in todos_los_productos:
                        nombre_base = p['name'].split()[0].lower() # Toma la primera palabra del producto (ej: "Foxiprid")
                        if nombre_base in texto_ia and len(nombre_base) > 3:
                            sugeridos.append(p)
                st.session_state.prods_filtrados = sugeridos[:4]
                st.rerun()
            except: st.error("Error en comunicación con IA.")

if st.session_state.chat_history:
    st.markdown("---")
    st.info(st.session_state.chat_history[-1]["parts"][0])
    user_reply = st.chat_input("¿Alguna duda técnica? Responde aquí...")
    if user_reply:
        with st.spinner("Consultando..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_reply)
            st.session_state.chat_history.append({"role": "user", "parts": [user_reply]})
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
            st.rerun()

# 4. TIENDA DINÁMICA
st.divider()
if st.session_state.prods_filtrados:
    st.markdown("### 🛒 Soluciones Específicas Detectadas")
    mostrar = st.session_state.prods_filtrados
else:
    st.markdown("### 🛒 Productos Destacados")
    mostrar = todos_los_productos[:4] if todos_los_productos else []

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            if p.get('image_128'):
                st.markdown(f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">', unsafe_allow_html=True)
            nombre_p = p['name'].split('(')[0].strip()
            st.markdown(f"**{nombre_p}**")
            st.write(f"RD$ {p['list_price']:,.2f}")
            link_p = f"https://wa.me/18295624653?text={urllib.parse.quote('Info sobre: ' + nombre_p)}"
            st.link_button("🛒 Cotizar", link_p, use_container_width=True)

# 5. REGISTRO Y 6. LOGOS
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
