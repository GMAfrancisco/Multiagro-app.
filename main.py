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
# Inicializamos las variables de estado al inicio absoluto para evitar reinicios por refresco de Streamlit
if "user_verified" not in st.session_state:
    st.session_state.user_verified = False
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "GRATIS"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state:
    st.session_state.prods_filtrados = []

URL_FONDO_HOJAS = "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1200"

# --- CSS DE ALTA VISIBILIDAD (PERSONALIZACIÓN CORPORATIVA) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; }}
    
    /* Visibilidad de Inputs y Placeholders */
    input::placeholder {{ color: #000000 !important; opacity: 1 !important; }}
    [data-testid="stFileUploadDropzone"] div, [data-testid="stFileUploadDropzone"] label, 
    [data-testid="stFileUploadDropzone"] span, [data-testid="stFileUploaderFileName"] {{ color: #000000 !important; }}
    [data-testid="stFileUploadDropzone"] button {{ color: #000000 !important; background-color: #f0f2f6 !important; }}
    
    /* Pestañas Blancas y Negritas */
    .stTabs [data-baseweb="tab"] p {{ color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem; }}
    
    /* Título LOGIN en una sola línea */
    .titulo-single-line {{ 
        text-align: center; 
        color: white; 
        white-space: nowrap; 
        font-size: 2.2rem; 
        font-weight: bold; 
        margin: 20px 0; 
    }}
    
    /* CAJA DE ANÁLISIS: FORZAR LETRAS BLANCAS Y DISEÑO PROFESIONAL */
    .diag-box {{ 
        background: #161B22; 
        padding: 30px; 
        border-radius: 15px; 
        border-left: 6px solid #25D366; 
        color: #FFFFFF !important; 
        line-height: 1.7; 
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    .diag-box p, .diag-box span, .diag-box li, .diag-box h1, .diag-box h2, .diag-box h3, .diag-box strong {{
        color: #FFFFFF !important;
    }}

    h1, h2, h3, h4, .stMarkdown p, label {{ color: #FFFFFF !important; }}
    
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 50px 20px; border-radius: 20px; text-align: center; margin-bottom: 30px; border: 1px solid #3E3E4A;
    }}
    
    /* Botones Estilo Multiagro */
    div.stButton > button {{ 
        background-color: #25D366 !important; 
        color: #FFFFFF !important; 
        border-radius: 25px !important; 
        font-weight: bold !important; 
        border: none !important;
        padding: 10px 25px !important;
    }}
    
    .product-img {{ width: 100%; height: 160px; object-fit: contain; background: white; border-radius: 10px; padding: 10px; }}

    /* Footer Logos con fondo blanco */
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

# --- FUNCIONES DE BACKEND (ODOO Y CRM) ---
def reset_analisis():
    st.session_state.chat_history = []
    st.session_state.prods_filtrados = []

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
        
        st.markdown('<div class="titulo-single-line">Diagnóstico Experto</div>', unsafe_allow_html=True)
        u_email = st.text_input("Correo electrónico corporativo:", placeholder="usuario@grupomultiagro.com")
        
        if st.button("ACCEDER AL SISTEMA"):
            if "@" in u_email:
                st.session_state.user_verified = True
                st.session_state.user_tier = "ILIMITADO" if "@grupomultiagro.com" in u_email.lower() else "GRATIS"
                st.rerun()
            else: st.error("Ingrese un correo válido.")
    st.stop()

# --- PANTALLA PRINCIPAL ---
todos_los_prods = get_odoo_prods()

st.markdown('<div class="header-banner"><h1>🔍 Diagnóstico Experto</h1><p>Grupo Multiagro | AgTech División</p></div>', unsafe_allow_html=True)

# 3. SECCIÓN: DIAGNÓSTICO CON JERARQUÍA DE DESCARTE (PASO A PASO)
cultivo_input = st.text_input("¿Qué cultivo analizamos?", placeholder="Ej: Ají, Tomate, Arroz...", on_change=reset_analisis)

img = None
t_gal, t_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with t_gal: img_gal = st.file_uploader("Subir imagen nítida del problema", type=['png', 'jpg', 'jpeg'])
with t_cam: img_cam = st.camera_input("Enfoque directamente al insecto o signo")

img = img_cam if img_cam else img_gal

if img is not None:
    if st.button("🚀 INICIAR ANÁLISIS PROFUNDO", type="primary", use_container_width=True):
        with st.spinner("Escaneando morfotipos de insectos y signos fitopatógenos..."):
            try:
                nombres_inv = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                # PROMPT DE MÁXIMO RIGOR (CADENA DE PENSAMIENTO FORENSE)
                prompt = f"""
                RESPONDE 100% EN ESPAÑOL TÉCNICO. 
                Eres el Especialista Senior en Protección de Cultivos de Grupo Multiagro. 
                Tu misión es detectar la causa biótica primaria en la imagen de {cultivo_input}.
                
                PROTOCOLO DE DESCARTE (ORDEN OBLIGATORIO):
                1. ESCANEO ENTOMOLÓGICO: Busca cuerpos de insectos, ácaros, larvas o huevos. (Ej: Busca Trips en los pétalos).
                2. ESCANEO PATOLÓGICO: Busca micelios de hongos, esporas, cancros o exudados bacterianos.
                3. ESCANEO NUTRICIONAL: Solo si descartas vida animal o fúngica, analiza deficiencias (clorosis, necrosis).

                ESTRUCTURA DE RESPUESTA:
                - IDENTIFICACIÓN POSITIVA: Nombre común y técnico (Sé específico, no genérico).
                - NIVEL DE CERTEZA: % de confianza basado en evidencia visual.
                - DESCRIPCIÓN DEL DAÑO: Qué patrones de alimentación o infección ves.
                - RECOMENDACIÓN MULTIAGRO: Elige 4 productos de esta lista: {nombres_inv}.
                - PREGUNTAS DE CAMPO: 2 preguntas para confirmar el diagnóstico.
                - PLAN DE ACCIÓN: Protocolo de manejo inmediato.
                """
                res = model.generate_content([prompt, Image.open(img)])
                texto_ia = res.text
                
                # FILTRADO DE PRODUCTOS BASADO EN TEXTO IA
                texto_ia_lower = texto_ia.lower()
                sugeridos, vistos = [], set()
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
            except Exception as e: st.error(f"Error técnico: {e}")

# MOSTRAR RESULTADO Y CHAT INTERACTIVO
if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[-1]['parts'][0]}</div>", unsafe_allow_html=True)
    
    user_reply = st.chat_input("Escribe aquí para profundizar en el diagnóstico...")
    if user_reply:
        with st.spinner("Consultando al experto..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_reply + " (Continúa en español técnico profesional)")
            st.session_state.chat_history.append({"role": "user", "parts": [user_reply]})
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
            st.rerun()

# 4. TIENDA DINÁMICA DE PRODUCTOS ODOO
st.divider()
st.markdown("### 🛒 Insumos Recomendados para este Caso")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])
if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f'data:image/png;base64,{p["image_128"]}' if p.get('image_128') else ""
            st.markdown(f'<img src="{img_b64}" class="product-img">', unsafe_allow_html=True)
            st.markdown(f"**{p['name'].split('(')[0].strip()}**")
            st.write(f"RD$ {p['list_price']:,.2f}")
            st.link_button("🟢 Cotizar WhatsApp", f"https://wa.me/18295624653?text=Cotizar: {urllib.parse.quote(p['name'])}", use_container_width=True)

# 5. REGISTRO CRM COMPLETO (32 PROVINCIAS RD)
st.divider()
st.markdown("### 👤 Registro de Productor")
provincias = ["Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "Elías Piña", "El Seibo", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"]
with st.form("registro_crm"):
    c1, c2 = st.columns(2)
    nom = c1.text_input("Nombre y Apellido *")
    tel = c1.text_input("WhatsApp / Teléfono *")
    ema = c2.text_input("Email (Opcional)")
    prov = c2.selectbox("Provincia", provincias)
    if st.form_submit_button("✅ COMPLETAR REGISTRO"):
        if nom and tel:
            if registrar_en_odoo(nom, ema, tel, prov): st.success("¡Registrado con éxito!")
            else: st.error("Error al conectar con Odoo.")
        else: st.warning("Nombre y Teléfono son campos obligatorios.")

# --- FOOTER DE MARCAS ---
st.divider()
st.markdown("<p style='text-align:center; color:#FFFFFF; font-weight:bold;'>Marcas Grupo Multiagro</p>", unsafe_allow_html=True)
logos = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div class="footer-white">'
for m in logos:
    if os.path.exists(m):
        with open(m, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
