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

# --- BLOQUE DE APARIENCIA (VISIBILIDAD EXTREMA Y DISEÑO MODERNO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* 1. CARGADOR DE ARCHIVOS: FORZAR TEXTO NEGRO EN TODAS LAS CAPAS */
    [data-testid="stFileUploadDropzone"] {
        background-color: #F0F2F6 !important;
        border-radius: 20px;
        border: 2px dashed #007BFF !important;
    }
    /* Selector universal para el texto dentro del cargador */
    [data-testid="stFileUploadDropzone"] * {
        color: #000000 !important;
    }

    /* 2. BOTONES: TEXTO NEGRO TOTAL */
    [data-testid="stBaseButton-secondary"] p, 
    [data-testid="stBaseButton-primary"] p,
    .stButton button p,
    .stFormSubmitButton button p {
        color: #000000 !important;
        font-weight: bold !important;
        margin-bottom: 0px !important;
    }
    
    /* Fondo de los botones */
    div.stButton > button, div.stFormSubmitButton > button, a[data-testid="stBaseButton-secondary"] {
        background-color: #007BFF !important;
        color: #000000 !important;
        border-radius: 30px !important;
        font-weight: bold !important;
        border: none !important;
        height: 45px !important;
    }

    /* 3. Tarjetas de Productos y Diagnóstico */
    .product-card {
        background-color: #1E1E26;
        border-radius: 25px;
        padding: 25px;
        border: 1px solid #3E3E4A;
        text-align: center;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .product-card:hover { transform: translateY(-5px); } 
    
    .product-img { 
        width: 100%; height: 180px; object-fit: contain; 
        background-color: white; border-radius: 20px; 
        padding: 10px; margin-bottom: 15px; 
    }
    .diag-box {
        background: #161B22; border-left: 8px solid #007BFF;
        padding: 25px; border-radius: 20px; margin-bottom: 30px;
    }

    /* 4. Líneas de Separación Elegantes */
    hr {
        border: 0; height: 1px;
        background: linear-gradient(to right, transparent, #3E3E4A, transparent);
        margin: 40px 0;
    }

    /* 5. Contenedor de Logos Inferiores (CORREGIDO TAMAÑO) */
    .logo-container { 
        display: flex; justify-content: center; align-items: center; 
        height: 100px; background: #FFFFFF; border-radius: 20px; padding: 15px;
    }
    /* CAMBIO AQUI: Altura fija de 60px para uniformidad, ancho automático */
    .logo-container img { height: 60px; width: auto; object-fit: contain; }
    
    /* Visibilidad de etiquetas generales */
    label, .stMarkdown, p, span { color: #FFFFFF !important; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #161B22; color: white; border-radius: 15px; }

    /* --- HERO BANNER CON TÍTULO CENTRADO --- */
    .hero-banner {
        background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1600&q=80');
        background-size: cover;
        background-position: center 30%;
        width: 100%;
        height: 220px;
        border-radius: 15px;
        margin-top: 15px;
        margin-bottom: 30px;
        display: flex;
        align-items: center; 
        justify-content: center; /* Título centrado */
    }
    
    .hero-title {
        color: #FFFFFF !important;
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.6);
        display: flex;
        align-items: center;
        gap: 15px; 
    }
    </style>
    """, unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []

# --- FUNCIONES DE INTEGRACIÓN (PRESERVADAS) ---
def get_odoo_prods():
    try:
        url, db, user, key = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"], st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 80})
            return models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
    except: return None

def registrar_cliente_odoo(nombre, email, telefono, lugar):
    try:
        url, db, user, key = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"], st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            # Se envía la provincia en el campo 'comment' (notas)
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{'name': nombre, 'email': email, 'phone': telefono, 'comment': f'App AgTech Multiagro | Provincia: {lugar}'}])
    except: return None

def enviar_aviso_email(nombre, email, tel, lugar):
    try:
        rem, pas = st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = rem, st.secrets["EMAIL_RECEIVER"], f"🚀 Nuevo Registro: {nombre}"
        msg.attach(MIMEText(f"Nombre: {nombre}\nEmail: {email}\nTel: {tel}\nProvincia: {lugar}", 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(); server.login(rem, pas); server.send_message(msg); server.quit()
        return True
    except: return False

# --- CUERPO DE LA APP ---
_, mid, _ = st.columns([1, 2, 1])
with mid:
    for f in sorted(os.listdir(".")):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

todos_los_prods = get_odoo_prods()

# 3. SECCIÓN: DIAGNÓSTICO EXPERTO
st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">🔍 Diagnóstico Experto</h1>
    </div>
""", unsafe_allow_html=True)

cultivo_input = st.text_input("¿Qué cultivo o planta estamos analizando?", placeholder="Ej: Arroz, Tomate, Aguacate...")

tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with tab_gal: img_gal = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'], key="uploader_gal")
with tab_cam: img_cam = st.camera_input("Tomar foto")

img = img_cam if img_cam else img_gal

if img is not None:
    if st.button("🚀 INICIAR ASESORÍA COMPLETA", type="primary", use_container_width=True):
        with st.spinner("Analizando..."):
            try:
                nombres_odoo = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                prompt = f"""
                RESPONDE 100% EN ESPAÑOL. Eres Fitopatólogo y Entomólogo de Multiagro. 
                CULTIVO: {cultivo_input if cultivo_input else 'No especificado'}.
                1. IDENTIFICACIÓN POSITIVA: Nombre común y técnico de la plaga/hongo con % de certeza.
                2. MANEJO QUÍMICO: Elige los 4 mejores de esta lista: {nombres_odoo}. Pon nombres en NEGRITAS.
                3. SEGURIDAD: Advierte leer la etiqueta del fabricante para dosis y periodos de carencia.
                4. LABORES CULTURALES: Describe labores de campo específicas para erradicar esto.
                5. INTERACCIÓN: Haz 2 preguntas clave para confirmar el diagnóstico.
                """
                
                res = model.generate_content([prompt, Image.open(img)])
                
                texto_ia_lower = res.text.lower()
                sugeridos, vistos = [], set()
                if todos_los_prods:
                    for p in todos_los_prods:
                        primera_palabra = p['name'].split()[0].lower()
                        if primera_palabra in texto_ia_lower and primera_palabra not in vistos and len(primera_palabra) > 3:
                            sugeridos.append(p); vistos.add(primera_palabra)
                        if len(sugeridos) >= 4: break
                
                st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
                st.session_state.prods_filtrados = sugeridos
                st.rerun()
            except Exception as e:
                if "rerun" not in str(e).lower(): st.error(f"Error: {e}")

if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[-1]['parts'][0]}</div>", unsafe_allow_html=True)
    st.chat_input("¿Dudas sobre el manejo?")

# 4. TIENDA DINÁMICA
st.divider()
st.markdown("<h3 style='color: #007BFF;'>🛒 Soluciones Sugeridas</h3>", unsafe_allow_html=True)
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
            st.markdown(f"""
                <div class="product-card">
                    {img_b64}
                    <h4 style='font-size: 0.9rem; margin-bottom: 5px;'>{p['name'].split('(')[0].strip()}</h4>
                    <p style='color: #007BFF; font-weight: bold;'>RD$ {p['list_price']:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            st.link_button("Cotizar", f"https://wa.me/18295624653?text=Info: {p['name']}", use_container_width=True)

# 5. REGISTRO
st.divider()
st.markdown("### 👤 Registro de Productor")

# Lista de provincias (sin cambios)
provincias_rd = ["Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"]

if 'reg_ok' not in st.session_state:
    with st.form("form_registro"):
        nom = st.text_input("Nombre completo *")
        ema = st.text_input("Correo electrónico")
        tel = st.text_input("WhatsApp / Teléfono *")
        lugar = st.selectbox("Lugar (Provincia) *", provincias_rd)
        
        if st.form_submit_button("✅ Regístrame"):
            if nom and tel and lugar:
                if registrar_cliente_odoo(nom, ema, tel, lugar):
                    enviar_aviso_email(nom, ema, tel, lugar)
                    st.session_state['reg_ok'] = nom
                    st.rerun()
else:
    st.success(f"Bienvenido, {st.session_state['reg_ok']}!")

# 6. LOGOS FINALES
st.divider()
# CAMBIO AQUI: Se agregó el título centrado antes de los logos
st.markdown("<h4 style='text-align: center; color: #007BFF; margin-bottom: 20px;'>Empresas Grupo Multiagro</h4>", unsafe_allow_html=True)

l_cols = st.columns(5)
logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
for i, l_file in enumerate(logos_list):
    with l_cols[i]:
        if os.path.exists(l_file):
            with open(l_file, "rb") as f: b64_logo = base64.b64encode(f.read()).decode()
            st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{b64_logo}"></div>', unsafe_allow_html=True)
