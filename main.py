import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import base64
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
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

# --- CSS DE ALTA VISIBILIDAD (CORRECCIÓN DE TEXTOS INVISIBLES) ---
st.markdown(f"""
    <style>
    /* Fondo General */
    .stApp {{ background-color: #0E1117; }}
    
    /* Forzar texto BLANCO en todo el cuerpo, párrafos, etiquetas y títulos */
    html, body, [data-testid="stWidgetLabel"], .stMarkdown, p, span, label, h1, h2, h3, h4 {{
        color: #FFFFFF !important;
        font-weight: 500;
    }}
    
    /* ARREGLO PARA EL FILE UPLOADER (Instrucciones visibles) */
    [data-testid="stFileUploadDropzone"] {{
        background-color: #f0f2f6 !important;
        border: 2px dashed #25D366 !important;
    }}
    [data-testid="stFileUploadDropzone"] div, 
    [data-testid="stFileUploadDropzone"] label, 
    [data-testid="stFileUploadDropzone"] span {{
        color: #000000 !important; /* Texto negro sobre fondo claro del uploader */
    }}

    /* Botones Estilo WhatsApp/Multiagro con Texto Blanco */
    div.stButton > button {{
        background-color: #25D366 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
        padding: 10px !important;
    }}
    
    /* Caja de Diagnóstico */
    .diag-box {{ 
        background: #161B22; 
        padding: 30px; 
        border-radius: 15px; 
        border-left: 6px solid #25D366; 
        color: #FFFFFF !important; 
        line-height: 1.7; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    .diag-box * {{ color: #FFFFFF !important; }}

    /* Inputs (Fondo oscuro, texto blanco) */
    .stTextInput>div>div>input {{
        color: #FFFFFF !important;
        background-color: #1E1E26 !important;
    }}
    input::placeholder {{ color: #cccccc !important; }}

    /* Banner */
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 50px 20px; border-radius: 20px; text-align: center; margin-bottom: 30px; border: 1px solid #3E3E4A;
    }}
    
    .product-card {{
        background:#1E1E26; padding:15px; border-radius:15px; border:1px solid #3E3E4A; text-align:center;
    }}
    .product-img {{ width: 100%; height: 160px; object-fit: contain; background: white; border-radius: 10px; padding: 10px; }}

    /* Footer Marcas */
    .footer-white {{ 
        background-color: #FFFFFF !important; 
        padding: 25px; 
        border-radius: 15px; 
        display: flex; 
        justify-content: space-around; 
        align-items: center; 
        flex-wrap: wrap; 
        margin-top: 30px; 
    }}
    .footer-white img {{ max-height: 60px; width: auto; margin: 15px; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
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

# --- LOGIN ---
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

# --- APP PRINCIPAL ---
todos_los_prods = get_odoo_prods()
st.markdown('<div class="header-banner"><h1>🔍 Diagnóstico Experto</h1><p>Prioridad: Insectos > Hongos > Nutrición</p></div>', unsafe_allow_html=True)

cultivo_input = st.text_input("¿Qué cultivo analizamos?", placeholder="Ej: Ají, Tomate, Arroz...")
t_gal, t_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with t_gal: img_gal = st.file_uploader("Arrastra aquí la imagen de la plaga", type=['png', 'jpg', 'jpeg'])
with t_cam: img_cam = st.camera_input("Toma una foto del signo")

img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ANÁLISIS PROFUNDO"):
    with st.spinner("Buscando insectos y patógenos en el tejido..."):
        try:
            nombres_inv = [p['name'] for p in todos_los_prods]
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            prompt = f"""
            RESPONDE 100% EN ESPAÑOL. Eres un Patólogo y Entomólogo de Grupo Multiagro.
            Analiza la imagen de {cultivo_input} buscando SIGNOS de vida antes que síntomas.
            
            JERARQUÍA:
            1. ENTOMOLOGÍA: Busca insectos (Trips, Áfidos, Ácaros).
            2. PATOLOGÍA: Busca micelios o esporas.
            3. NUTRICIÓN: Solo si descartas vida tras escaneo pixelar.

            ESTRUCTURA:
            - IDENTIFICACIÓN POSITIVA: Nombre común y técnico.
            - CERTEZA: % de confianza.
            - PRODUCTOS: Elige 4 de esta lista: {nombres_inv}.
            - PLAN DE ACCIÓN: Labores culturales y manejo.
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

# --- TIENDA (BOTONES COTIZAR) ---
st.divider()
st.markdown("### 🛒 Insumos Recomendados")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else todos_los_prods[:4]
if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f"data:image/png;base64,{p['image_128']}" if p.get('image_128') else ""
            st.markdown(f'<div class="product-card"><img src="{img_b64}" class="product-img"><p style="font-weight:bold; color:white; margin-top:10px;">{p["name"][:35]}</p><p style="color:#25D366; font-weight:bold;">RD$ {p["list_price"]:,.2f}</p></div>', unsafe_allow_html=True)
            st.link_button("🟢 Cotizar WhatsApp", f"https://wa.me/18295624653?text=Cotizar: {urllib.parse.quote(p['name'])}")

# --- REGISTRO CRM (32 PROVINCIAS) ---
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

# FOOTER
st.divider()
st.markdown("<p style='text-align:center;'>Marcas Grupo Multiagro</p>", unsafe_allow_html=True)
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div class="footer-white">'
for m in logos:
    if os.path.exists(m):
        with open(m, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
