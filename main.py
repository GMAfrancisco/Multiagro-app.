import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import base64
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera instrucción)
st.set_page_config(
    page_title="Grupo Multiagro | AgTech Diagnóstico",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LÓGICA DE SESIÓN (PERSISTENCIA TOTAL Y SEGURIDAD) ---
if "user_verified" not in st.session_state:
    st.session_state.user_verified = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state:
    st.session_state.prods_filtrados = []

URL_FONDO_HOJAS = "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1200"

# --- CSS DE ALTA VISIBILIDAD (ESTILO CORPORATIVO MULTIAGRO) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; }}
    h1, h2, h3, h4, p, span, label, .stMarkdown {{ color: #FFFFFF !important; }}
    
    /* Visibilidad de Inputs y Placeholders */
    input::placeholder {{ color: #000000 !important; opacity: 1 !important; }}
    [data-testid="stFileUploadDropzone"] div, [data-testid="stFileUploadDropzone"] label, 
    [data-testid="stFileUploadDropzone"] span, [data-testid="stFileUploaderFileName"] {{ color: #000000 !important; }}
    [data-testid="stFileUploadDropzone"] button {{ color: #000000 !important; background-color: #f0f2f6 !important; }}
    
    /* Pestañas Blancas y Negritas */
    .stTabs [data-baseweb="tab"] p {{ color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem; }}
    
    /* CAJA DE ANÁLISIS: FORZAR LETRAS BLANCAS */
    .diag-box {{ 
        background: #161B22; padding: 30px; border-radius: 15px; border-left: 6px solid #25D366; 
        color: #FFFFFF !important; line-height: 1.7; font-size: 1.1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    .diag-box * {{ color: #FFFFFF !important; }}
    
    .product-img {{ width: 100%; height: 160px; object-fit: contain; background: white; border-radius: 10px; padding: 10px; }}
    
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 50px 20px; border-radius: 20px; text-align: center; margin-bottom: 30px; border: 1px solid #3E3E4A;
    }}
    div.stButton > button {{ background-color: #25D366 !important; color: white !important; border-radius: 25px !important; font-weight: bold !important; border: none; }}
    
    .footer-white {{ background-color: #FFFFFF !important; padding: 25px; border-radius: 15px; display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; margin-top: 30px; }}
    .footer-white img {{ max-height: 60px; width: auto; margin: 15px; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE BACKEND (ODOO Y CRM) ---
def get_odoo_prods():
    try:
        url, db, user, key = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"], st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 150})
            return models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
    except: return []

def registrar_en_odoo(nombre, email, telefono, provincia):
    try:
        url, db, user, key = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"], st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{'name': nombre, 'email': email, 'phone': telefono, 'comment': f'App Diagnóstico - Prov: {provincia}'}])
    except: return None

# --- FLUJO DE CONTROL: LOGIN ---
if not st.session_state.user_verified:
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for f in os.listdir("."):
            if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)
        st.markdown("<h2 style='text-align:center;'>Acceso AgroTech</h2>", unsafe_allow_html=True)
        u_email = st.text_input("Correo electrónico:", placeholder="usuario@grupomultiagro.com")
        if st.button("INGRESAR AL SISTEMA"):
            if "@" in u_email:
                st.session_state.user_verified = True
                st.rerun()
    st.stop()

# --- APP PRINCIPAL ---
todos_los_prods = get_odoo_prods()
st.markdown('<div class="header-banner"><h1>🔍 Diagnóstico Experto</h1><p>Jerarquía: Plagas > Hongos > Nutrición</p></div>', unsafe_allow_html=True)

# 3. SECCIÓN DIAGNÓSTICO
cultivo_input = st.text_input("¿Qué cultivo analizamos?", placeholder="Ej: Ají, Tomate, Arroz...")
img = None
tab1, tab2 = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with tab1: img_gal = st.file_uploader("Subir imagen nítida", type=['png', 'jpg', 'jpeg'])
with tab2: img_cam = st.camera_input("Enfoque al insecto o signo")

img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
    with st.spinner("Escaneando morfotipos de insectos y patógenos..."):
        try:
            nombres_inv = [p['name'] for p in todos_los_prods]
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            # PROMPT CON PRIORIDAD DE DESCARTE (SOLUCIÓN A "NO DETECTA INSECTOS")
            prompt = f"""
            RESPONDE 100% EN ESPAÑOL PROFESIONAL. Eres un Patólogo y Entomólogo de Grupo Multiagro.
            Analiza la imagen de {cultivo_input} buscando SIGNOS de vida antes que síntomas de la planta.
            
            JERARQUÍA DE ANÁLISIS:
            1. ESCANEO ENTOMOLÓGICO: Busca cuerpos alargados (Trips), puntos móviles (Ácaros) o larvas. Si hay insectos, nómbralos.
            2. ESCANEO PATOLÓGICO: Busca micelios de hongos, esporas o exudados bacterianos.
            3. ESCANEO NUTRICIONAL: Solo si descartas lo anterior tras análisis pixelar, evalúa deficiencias.

            ESTRUCTURA DE RESPUESTA:
            - IDENTIFICACIÓN POSITIVA: Nombre común y técnico (Sé agresivo en la detección).
            - NIVEL DE CERTEZA: % de seguridad.
            - DESCRIPCIÓN DEL DAÑO: Qué patrones de alimentación o infección ves.
            - RECOMENDACIÓN MULTIAGRO: Elige 4 productos de esta lista: {nombres_inv}.
            - PREGUNTAS DE CAMPO: 2 preguntas para precisar el diagnóstico.
            - PLAN DE ACCIÓN: Protocolo inmediato.
            """
            res = model.generate_content([prompt, Image.open(img)])
            
            # Guardado correcto para evitar TypeError
            st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
            
            # Filtrado inteligente de productos
            ia_text = res.text.lower()
            sugeridos, vistos = [], set()
            for p in todos_los_prods:
                p_name = p['name'].lower().split()[0]
                if p_name in ia_text and len(p_name) > 3 and p_name not in vistos:
                    sugeridos.append(p)
                    vistos.add(p_name)
                if len(sugeridos) >= 4: break
            st.session_state.prods_filtrados = sugeridos
            st.rerun()
        except Exception as e:
            st.error(f"Error técnico: {e}")

# MOSTRAR RESULTADO Y CHAT
if st.session_state.chat_history:
    # Acceso seguro al último mensaje
    ultimo_msg = st.session_state.chat_history[-1]["parts"][0]
    st.markdown(f"<div class='diag-box'>{ultimo_msg}</div>", unsafe_allow_html=True)
    
    # CHAT INTERACTIVO (Recuperado)
    user_reply = st.chat_input("Pregunta al técnico sobre este resultado...")
    if user_reply:
        with st.spinner("Analizando respuesta técnica..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_reply + " (Responde en español técnico)")
            st.session_state.chat_history.append({"role": "user", "parts": [user_reply]})
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
            st.rerun()

# 4. TIENDA DINÁMICA
st.divider()
st.markdown("### 🛒 Insumos Sugeridos")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else todos_los_prods[:4]
if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f"data:image/png;base64,{p['image_128']}" if p.get('image_128') else ""
            st.markdown(f'<img src="{img_b64}" class="product-img">', unsafe_allow_html=True)
            st.write(f"**{p['name']}**")
            st.write(f"RD$ {p['list_price']:,.2f}")
            st.link_button("🛒 Cotizar", f"https://wa.me/18295624653?text=Cotizar: {urllib.parse.quote(p['name'])}")

# 5. REGISTRO CRM (32 PROVINCIAS RD)
st.divider()
st.markdown("### 👤 Registro de Productor")
provincias = ["Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"]
with st.form("crm_reg"):
    c1, c2 = st.columns(2)
    nom_crm = c1.text_input("Nombre Completo *")
    tel_crm = c1.text_input("WhatsApp *")
    ema_crm = c2.text_input("Correo (Opcional)")
    prov_crm = c2.selectbox("Provincia", provincias)
    if st.form_submit_button("✅ REGISTRAR DATOS"):
        if nom_crm and tel_crm:
            if registrar_en_odoo(nom_crm, ema_crm, tel_crm, prov_crm): st.success("¡Registrado!")
            else: st.error("Error al conectar con Odoo.")

# FOOTER LOGOS
st.divider()
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div class="footer-white">'
for m in logos:
    if os.path.exists(m):
        with open(m, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
