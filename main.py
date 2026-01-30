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

# --- LÓGICA DE SESIÓN (PERSISTENCIA TOTAL) ---
if "user_verified" not in st.session_state:
    st.session_state.user_verified = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state:
    st.session_state.prods_filtrados = []

URL_FONDO_HOJAS = "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1200"

# --- CSS DE ALTA VISIBILIDAD (CORRECCIÓN TOTAL DE BOTONES E INPUTS) ---
st.markdown(f"""
    <style>
    /* Fondo y Textos Base */
    .stApp {{ background-color: #0E1117; }}
    h1, h2, h3, h4, p, span, label, div {{ color: #FFFFFF !important; }}
    
    /* CORRECCIÓN FILE UPLOADER (Drag and Drop) */
    [data-testid="stFileUploadDropzone"] {{
        background-color: #262730 !important;
        border: 2px dashed #25D366 !important;
    }}
    [data-testid="stFileUploadDropzone"] div, 
    [data-testid="stFileUploadDropzone"] label, 
    [data-testid="stFileUploadDropzone"] span {{
        color: #FFFFFF !important;
    }}

    /* BOTONES (Cotizar, Iniciar, Guardar Registro) - TEXTO BLANCO FORZADO */
    button, div.stButton > button, div.stFormSubmitButton > button, .stDownloadButton > button {{
        background-color: #25D366 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100% !important;
        height: 45px !important;
    }}
    
    /* Selector específico para el texto dentro de los botones de Streamlit */
    button p {{
        color: #FFFFFF !important;
        font-size: 1rem !important;
        margin: 0 !important;
    }}

    /* CAJA DE ANÁLISIS */
    .diag-box {{ 
        background: #161B22; padding: 30px; border-radius: 15px; 
        border-left: 6px solid #25D366; color: #FFFFFF !important; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    .diag-box * {{ color: #FFFFFF !important; }}

    /* PRODUCTOS */
    .product-card {{
        background:#1E1E26; padding:15px; border-radius:15px; 
        border:1px solid #3E3E4A; text-align:center; margin-bottom: 10px;
    }}
    .product-img {{ width: 100%; height: 160px; object-fit: contain; background: white; border-radius: 10px; padding: 10px; }}

    /* INPUTS */
    input {{ color: #FFFFFF !important; background-color: #1E1E26 !important; }}
    .stSelectbox div {{ color: #FFFFFF !important; }}
    
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 50px 20px; border-radius: 20px; text-align: center; margin-bottom: 30px; border: 1px solid #3E3E4A;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE ODOO ---
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
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{'name': nombre, 'email': email, 'phone': telefono, 'comment': f'Provincia: {provincia}'}])
    except: return None

# --- ACCESO / LOGIN ---
if not st.session_state.user_verified:
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for f in os.listdir("."):
            if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)
        st.markdown("<h2 style='text-align:center;'>Acceso AgroTech</h2>", unsafe_allow_html=True)
        u_email = st.text_input("Ingresa tu correo:", placeholder="usuario@grupomultiagro.com")
        if st.button("INGRESAR"):
            if "@" in u_email:
                st.session_state.user_verified = True
                st.rerun()
    st.stop()

# --- PANTALLA PRINCIPAL ---
todos_los_prods = get_odoo_prods()
st.markdown('<div class="header-banner"><h1>🔍 Diagnóstico Experto</h1><p>Jerarquía: Plagas > Hongos > Nutrición</p></div>', unsafe_allow_html=True)

cultivo_input = st.text_input("¿Qué cultivo analizamos?", placeholder="Ej: Tomate, Ají, Arroz...")
t_gal, t_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with t_gal: 
    img_gal = st.file_uploader("Sube o arrastra aquí la imagen de la plaga", type=['png', 'jpg', 'jpeg'])
with t_cam: 
    img_cam = st.camera_input("Captura el signo")

img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ANÁLISIS"):
    with st.spinner("Escaneando en busca de insectos y patógenos..."):
        try:
            nombres_inv = [p['name'] for p in todos_los_prods]
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            prompt = f"""
            RESPONDE 100% EN ESPAÑOL TÉCNICO. Eres un experto de Grupo Multiagro.
            Analiza la imagen de {cultivo_input} con rigor microscópico.
            
            JERARQUÍA DE DIAGNÓSTICO:
            1. ENTOMOLOGÍA: Busca insectos (Trips, Ácaros, Áfidos) o restos biológicos.
            2. PATOLOGÍA: Busca micelios de hongos, esporas o bacterias.
            3. NUTRICIÓN: Solo si descartas lo anterior tras análisis pixelar.

            ESTRUCTURA DE RESPUESTA:
            1. IDENTIFICACIÓN POSITIVA: Nombre común y científico.
            2. NIVEL DE CERTEZA: % de confianza.
            3. MANEJO QUÍMICO: Elige 4 productos de esta lista: {nombres_inv}.
            4. ADVERTENCIA TÉCNICA: Leer etiqueta.
            5. LABORES CULTURALES: 5 tareas.
            6. INTERACCIÓN: 2 preguntas técnicas.
            """
            res = model.generate_content([prompt, Image.open(img)])
            st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
            
            ia_text = res.text.lower()
            sugeridos = []
            for p in todos_los_prods:
                p_name = p['name'].lower().split()[0]
                if p_name in ia_text and len(p_name) > 3:
                    sugeridos.append(p)
                if len(sugeridos) >= 4: break
            st.session_state.prods_filtrados = sugeridos
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[-1]['parts'][0]}</div>", unsafe_allow_html=True)

# --- TIENDA (BOTONES COTIZAR WHATSAPP) ---
st.divider()
st.markdown("### 🛒 Insumos Recomendados")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else todos_los_prods[:4]
if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f"data:image/png;base64,{p['image_128']}" if p.get('image_128') else ""
            st.markdown(f'<div class="product-card"><img src="{img_b64}" class="product-img"><p style="font-weight:bold;">{p["name"][:35]}</p><p style="color:#25D366; font-weight:bold;">RD$ {p["list_price"]:,.2f}</p></div>', unsafe_allow_html=True)
            st.link_button("🟢 COTIZAR WHATSAPP", f"https://wa.me/18295624653?text=Cotizar: {urllib.parse.quote(p['name'])}")

# --- REGISTRO CRM ---
st.divider()
st.markdown("### 👤 Registrar Datos del Productor")
provincias = ["Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"]
with st.form("crm_form"):
    c1, c2 = st.columns(2)
    n = c1.text_input("Nombre Completo *")
    t = c1.text_input("WhatsApp *")
    e = c2.text_input("Correo")
    pr = c2.selectbox("Provincia", provincias)
    if st.form_submit_button("✅ GUARDAR REGISTRO"):
        if n and t:
            if registrar_en_odoo(n, e, t, pr): st.success("¡Registrado!")
            else: st.error("Error al conectar.")

# --- FOOTER ---
st.divider()
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div style="background-color: white; padding: 20px; border-radius: 15px; display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">'
for m in logos:
    if os.path.exists(m):
        with open(m, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}" style="max-height: 50px; margin: 10px;">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
