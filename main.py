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
    layout="wide"
)

# --- LÓGICA DE SESIÓN (PERSISTENCIA TOTAL) ---
if "user_verified" not in st.session_state:
    st.session_state.user_verified = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state:
    st.session_state.prods_filtrados = []

# --- CSS: CORRECCIÓN DE VISIBILIDAD MANTENIENDO TU ESTRUCTURA ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; }}
    
    /* Forzar texto blanco en etiquetas y párrafos */
    h1, h2, h3, h4, p, span, label {{ color: #FFFFFF !important; }}

    /* CORRECCIÓN FILE UPLOADER (Drag and Drop visible) */
    [data-testid="stFileUploadDropzone"] {{
        background-color: #262730 !important;
        border: 2px dashed #25D366 !important;
    }}
    [data-testid="stFileUploadDropzone"] div, 
    [data-testid="stFileUploadDropzone"] label, 
    [data-testid="stFileUploadDropzone"] span {{
        color: #FFFFFF !important;
    }}

    /* BOTONES: "Cotizar" y "Registrar" con LETRAS BLANCAS */
    button, div.stButton > button, div.stFormSubmitButton > button {{
        background-color: #25D366 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100% !important;
    }}
    
    /* Forzar texto blanco dentro de botones */
    button p, .stButton p, .stFormSubmitButton p {{
        color: #FFFFFF !important;
        margin: 0 !important;
        font-size: 1rem !important;
    }}

    /* Estilo del análisis (Caja de texto) */
    .diag-box {{ 
        background: #161B22; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 6px solid #25D366; 
        color: #FFFFFF !important; 
    }}
    .diag-box * {{ color: #FFFFFF !important; }}
    
    /* Estilo Tienda */
    .product-card {{
        background:#1E1E26; padding:15px; border-radius:15px; border:1px solid #3E3E4A; text-align:center;
    }}
    .product-img {{ width: 100%; height: 160px; object-fit: contain; background: white; border-radius: 10px; padding: 10px; }}
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

# --- LOGIN ORIGINAL ---
if not st.session_state.user_verified:
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for f in os.listdir("."):
            if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)
        st.markdown("<h2 style='text-align:center;'>Acceso AgroTech</h2>", unsafe_allow_html=True)
        u_email = st.text_input("Correo electrónico:", placeholder="usuario@grupomultiagro.com")
        if st.button("INGRESAR"):
            if "@" in u_email:
                st.session_state.user_verified = True
                st.rerun()
    st.stop()

# --- APP PRINCIPAL ---
todos_los_prods = get_odoo_prods()
st.markdown("## 🔍 Diagnóstico Fitosanitario")

# SECCIÓN DIAGNÓSTICO
cultivo_input = st.text_input("¿Qué cultivo analizamos?", placeholder="Ej: Tomate, Ají, Arroz...")
t_gal, t_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with t_gal: 
    img_gal = st.file_uploader("Arrastra aquí la imagen del problema", type=['png', 'jpg', 'jpeg'])
with t_cam: 
    img_cam = st.camera_input("Toma la foto")

img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ANÁLISIS"):
    with st.spinner("Escaneando plagas y patógenos..."):
        try:
            nombres_inv = [p['name'] for p in todos_los_prods]
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            prompt = f"""
            RESPONDE 100% EN ESPAÑOL. Eres un experto de Grupo Multiagro.
            Prioridad de análisis para {cultivo_input} (Busca signos antes que síntomas):
            1. PLAGAS (Busca insectos diminutos como Trips, ácaros o pulgones).
            2. HONGOS/BACTERIAS (Busca micelios, esporas o manchas).
            3. NUTRICIÓN (Solo si descartas lo anterior tras análisis pixelar).
            
            Estructura: Identificación técnica, Certeza %, 4 productos de {nombres_inv} y Plan de Acción.
            """
            res = model.generate_content([prompt, Image.open(img)])
            st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[-1]['parts'][0]}</div>", unsafe_allow_html=True)

# TIENDA DINÁMICA
st.divider()
st.markdown("### 🛒 Insumos Recomendados")
mostrar = todos_los_prods[:4] if todos_los_prods else []
if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f"data:image/png;base64,{p['image_128']}" if p.get('image_128') else ""
            st.markdown(f'<div class="product-card"><img src="{img_b64}" class="product-img"><p style="font-weight:bold;">{p["name"][:30]}</p></div>', unsafe_allow_html=True)
            st.link_button("🟢 COTIZAR WHATSAPP", f"https://wa.me/18295624653?text=Cotizar: {urllib.parse.quote(p['name'])}")

# REGISTRO CRM
st.divider()
st.markdown("### 👤 Registrar Datos del Productor")
provincias = ["Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"]
with st.form("crm_reg"):
    c1, c2 = st.columns(2)
    n = c1.text_input("Nombre Completo *")
    t = c1.text_input("WhatsApp *")
    ema = c2.text_input("Correo")
    pr = c2.selectbox("Provincia", provincias)
    if st.form_submit_button("✅ GUARDAR REGISTRO"):
        if n and t: st.success("¡Registrado!")

# FOOTER LOGOS
st.divider()
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div style="background-color: white; padding: 20px; border-radius: 15px; display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">'
for m in logos:
    if os.path.exists(m):
        with open(m, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}" style="max-height: 50px; margin: 10px;">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
