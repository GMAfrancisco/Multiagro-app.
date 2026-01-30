import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import base64
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera instrucción)
st.set_page_config(
    page_title="Grupo Multiagro | Diagnóstico Experto",
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

# --- CSS DE ALTA VISIBILIDAD (CORRECCIÓN DE TEXTOS INVISIBLES) ---
st.markdown(f"""
    <style>
    /* 1. FONDO Y TEXTOS GENERALES */
    .stApp {{ background-color: #0E1117; }}
    h1, h2, h3, h4, p, span, label, div {{ color: #FFFFFF !important; }}
    
    /* 2. CORRECCIÓN DEL CARGADOR DE ARCHIVOS (Drag and Drop) */
    [data-testid="stFileUploadDropzone"] {{
        background-color: #262730 !important;
        border: 2px dashed #25D366 !important;
    }}
    [data-testid="stFileUploadDropzone"] div, 
    [data-testid="stFileUploadDropzone"] label, 
    [data-testid="stFileUploadDropzone"] span {{
        color: #FFFFFF !important;
    }}

    /* 3. BOTONES (Cotizar, Iniciar, Guardar Registro) */
    button, div.stButton > button, div.stFormSubmitButton > button {{
        background-color: #25D366 !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100% !important;
        display: block !important;
        min-height: 45px;
    }}
    
    /* Forzar texto blanco dentro de botones de enlace y etiquetas de botones */
    .stButton p, .stDownloadButton p, .stFormSubmitButton p, button p {{
        color: #FFFFFF !important;
        margin: 0 !important;
    }}

    /* 4. CAJA DE RESULTADOS */
    .diag-box {{ 
        background: #161B22; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 6px solid #25D366; 
        color: #FFFFFF !important; 
    }}
    .diag-box * {{ color: #FFFFFF !important; }}

    /* 5. PRODUCTOS */
    .product-card {{
        background:#1E1E26; padding:15px; border-radius:15px; border:1px solid #3E3E4A; text-align:center;
    }}
    .product-img {{ width: 100%; height: 160px; object-fit: contain; background: white; border-radius: 10px; padding: 10px; }}

    /* 6. INPUTS Y SELECTS */
    input {{ color: #FFFFFF !important; background-color: #1E1E26 !important; }}
    .stSelectbox div {{ color: #FFFFFF !important; }}
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
st.markdown("## 🔍 Diagnóstico Fitosanitario")

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
            RESPONDE 100% EN ESPAÑOL. Eres un experto en entomología de Grupo Multiagro.
            Analiza la imagen de {cultivo_input} con jerarquía de prioridad:
            1. INSECTOS (Busca trips, ácaros, áfidos o daños de masticación).
            2. HONGOS/BACTERIAS (Busca micelios, esporas o manchas necróticas).
            3. NUTRICIÓN (Solo si no hay agentes bióticos presentes).

            Estructura tu respuesta así:
            - IDENTIFICACIÓN TÉCNICA: Nombre común y científico.
            - NIVEL DE CERTEZA: Porcentaje.
            - PRODUCTOS RECOMENDADOS: Elige 4 de esta lista: {nombres_inv}.
            - PLAN DE ACCIÓN: Pasos a seguir.
            """
            res = model.generate_content([prompt, Image.open(img)])
            st.session_state.chat_history = [{"role": "model", "parts": [res.text]}]
            
            # Filtrado de productos para la tienda
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

# --- TIENDA DINÁMICA ---
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
            else: st.error("Error al conectar con Odoo.")

# --- FOOTER MARCAS ---
st.divider()
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div style="background-color: white; padding: 20px; border-radius: 15px; display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">'
for m in logos:
    if os.path.exists(m):
        with open(m, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}" style="max-height: 50px; margin: 10px;">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
