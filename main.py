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

# URL del Banner de Hojas
URL_FONDO_HOJAS = "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80"

# CSS COMPLETO: LÍNEA GRÁFICA + TEXTOS BLANCOS + BOTONES
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; color: #FFFFFF; }}
    
    /* Banner de Hojas */
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 50px 20px; border-radius: 15px; text-align: center;
        margin-bottom: 25px; border: 1px solid #3E3E4A;
    }}

    /* Forzar textos blancos en labels y tabs */
    label, .stMarkdown, p, span, .stText, .stTabs [data-baseweb="tab"] p {{ 
        color: #FFFFFF !important; 
    }}

    /* Tarjetas de Productos Modernas */
    .product-card {{
        background-color: #1E1E26; border-radius: 15px; padding: 20px;
        border: 1px solid #3E3E4A; text-align: center; margin-bottom: 15px;
    }}
    .product-img {{ 
        width: 100%; height: 180px; object-fit: contain; 
        background-color: white; border-radius: 10px; 
        padding: 5px; margin-bottom: 10px; 
    }}

    /* Caja de Diagnóstico IA */
    .diag-box {{
        background: #161B22; border-left: 5px solid #007BFF;
        padding: 20px; border-radius: 10px; margin-bottom: 25px;
        color: #FFFFFF; font-size: 1.1rem;
    }}

    /* Botones Estilo Premium */
    div.stButton > button {{
        background-color: #007BFF !important; color: white !important;
        border-radius: 25px !important; width: 100%; border: none !important;
        font-weight: bold; text-transform: uppercase;
    }}

    /* Logos con fondo blanco para contraste */
    .logo-container {{ 
        display: flex; justify-content: center; align-items: center; 
        height: 80px; background: #FFFFFF; border-radius: 10px; 
        padding: 10px; margin-top: 10px;
    }}
    .logo-container img {{ max-height: 100%; max-width: 100%; object-fit: contain; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESIÓN Y PERMISOS ---
if "user_verified" not in st.session_state: st.session_state.user_verified = False
if "user_tier" not in st.session_state: st.session_state.user_tier = "GRATIS"
if "credits" not in st.session_state: st.session_state.credits = 2
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []

def verificar_acceso(email):
    email = email.lower().strip()
    dominios_vip = ["@grupomultiagro.com", "@mundoagricola.net"]
    if any(email.endswith(dom) for dom in dominios_vip):
        return "ILIMITADO", "Colaborador Corporativo"
    return "GRATIS", "Usuario Estándar (Créditos Limitados)"

# --- FUNCIONES DE INTEGRACIÓN (ODOO & EMAIL) ---
def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 80})
            return models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
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
                'name': nombre, 'email': email, 'phone': telefono, 'comment': 'App AgTech Multiagro'
            }])
    except: return None

def enviar_aviso_email(nombre, email, tel):
    try:
        rem, pas = st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = rem, st.secrets["EMAIL_RECEIVER"], f"🚀 Nuevo Registro: {nombre}"
        msg.attach(MIMEText(f"Nombre: {nombre}\nEmail: {email}\nTel: {tel}", 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(); server.login(rem, pas); server.send_message(msg); server.quit()
        return True
    except: return False

# --- PANTALLA DE ACCESO ---
if not st.session_state.user_verified:
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for f in os.listdir("."):
            if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
                st.image(f, use_container_width=True)
        st.subheader("Identificación de Usuario")
        user_email = st.text_input("Correo electrónico:", placeholder="ejemplo@grupomultiagro.com")
        if st.button("ACCEDER A LA PLATAFORMA"):
            if "@" in user_email and "." in user_email:
                tier, label = verificar_acceso(user_email)
                st.session_state.user_verified, st.session_state.user_tier, st.session_state.user_email = True, tier, user_email
                st.success(f"Sesión iniciada: {label}"); st.rerun()
            else: st.error("Ingresa un correo válido.")
    st.stop()

# --- CUERPO DE LA APP (SI ESTÁ VERIFICADO) ---
st.markdown(f"""<div class="header-banner"><h1 style="color: white; margin: 0;">🔍 Diagnóstico Experto</h1><p style="color: #E0E0E0;">Plan {st.session_state.user_tier}</p></div>""", unsafe_allow_html=True)

if st.session_state.user_tier == "GRATIS":
    st.info(f"📊 Tienes **{st.session_state.credits}** consultas gratuitas para hoy.")

todos_los_prods = get_odoo_prods()

# 3. SECCIÓN DIAGNÓSTICO
cultivo_input = st.text_input("Cultivo o planta a analizar:", placeholder="Ej: Tomate, Arroz...")
tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with tab_gal: img_gal = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam: img_cam = st.camera_input("Tomar foto")

img = img_cam if img_cam else img_gal

if img is not None:
    bloqueado = st.session_state.user_tier == "GRATIS" and st.session_state.credits <= 0
    btn_text = "🚀 INICIAR ASESORÍA COMPLETA" if not bloqueado else "🔒 CRÉDITOS AGOTADOS"
    
    if st.button(btn_text, disabled=bloqueado, type="primary", use_container_width=True):
        with st.spinner("IA analizando patología y catálogo..."):
            try:
                nombres_odoo = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                prompt = f"""RESPONDE 100% ESPAÑOL. Eres experto de Multiagro. Cultivo: {cultivo_input}. 
                1. IDENTIFICACIÓN: Nombre común y técnico con % certeza. 
                2. MANEJO QUÍMICO: Elige 4 de {nombres_odoo} en NEGRITAS. 
                3. SEGURIDAD: Advierte leer etiqueta del fabricante para dosis. 
                4. LABORES CULTURALES: Tareas físicas específicas de manejo. 
                5. INTERACCIÓN: 2 preguntas clave."""
                
                res = model.generate_content([prompt, Image.open(img)])
                texto_ia_lower = res.text.lower()
                
                # Filtrado inteligente
                sugeridos, vistos = [], set()
                if todos_los_prods:
                    for p in todos_los_prods:
                        p_name = p['name'].split()[0].lower()
                        if p_name in texto_ia_lower and p_name not in vistos and len(p_name) > 3:
                            sugeridos.append(p); vistos.add(p_name)
                        if len(sugeridos) >= 4: break
                
                st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
                st.session_state.prods_filtrados = sugeridos
                if st.session_state.user_tier == "GRATIS": st.session_state.credits -= 1
                st.rerun()
            except Exception as e:
                if "rerun" not in str(e).lower(): st.error(f"Error: {e}")

if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[-1]['parts'][0]}</div>", unsafe_allow_html=True)

# 4. TIENDA DINÁMICA
st.divider()
st.markdown("<h3 style='color: #007BFF;'>🛒 Soluciones Sugeridas</h3>", unsafe_allow_html=True)
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])
if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
            st.markdown(f'<div class="product-card">{img_b64}<h4 style="font-size:0.9rem;">{p["name"].split("(")[0].strip()}</h4><p style="color:#007BFF; font-weight:bold;">RD$ {p["list_price"]:,.2f}</p></div>', unsafe_allow_html=True)
            st.link_button("WhatsApp", f"https://wa.me/18295624653?text=Info: {p['name']}", use_container_width=True)

# 5. REGISTRO
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
                    st.session_state['reg_ok'] = nom; st.rerun()
else: st.success(f"Bienvenido, {st.session_state['reg_ok']}!")

# 6. LOGOS FINALES
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
l_cols = st.columns(5)
logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
for i, l_file in enumerate(logos_list):
    with l_cols[i]:
        if os.path.exists(l_file):
            with open(l_file, "rb") as f: b64_logo = base64.b64encode(f.read()).decode()
            st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{b64_logo}"></div>', unsafe_allow_html=True)
