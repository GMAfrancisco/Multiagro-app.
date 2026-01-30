import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import base64
import time

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera instrucción)
st.set_page_config(
    page_title="Grupo Multiagro | AgTech Diagnóstico",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LÓGICA DE SESIÓN (PERSISTENCIA BLINDADA) ---
# Inicializamos las variables de estado al inicio absoluto para evitar reinicios por refresco
if "user_verified" not in st.session_state:
    st.session_state.user_verified = False
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "GRATIS"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state:
    st.session_state.prods_filtrados = []

URL_FONDO_HOJAS = "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1200"

# --- CSS DE ALTA VISIBILIDAD (PERSONALIZACIÓN GRUPO MULTIAGRO) ---
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

# --- FUNCIONES DE BACKEND ---
def reset_analisis():
    st.session_state.chat_history = []
    st.session_state.prods_filtrados = []

def registrar_en_odoo(nombre, email, telefono, provincia):
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            return models.execute_kw(db, uid, key, 'res.partner', 'create', [{
                'name': nombre, 'email': email, 'phone': telefono, 
                'comment': f'Prospecto desde App Diagnóstico. Provincia: {provincia}'
            }])
    except Exception as e:
        st.error(f"Error de conexión Odoo: {e}")
        return None

def get_odoo_prods():
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
            ids = models.execute_kw(db, uid, key, 'product.template', 'search', [[['sale_ok','=',True]]], {'limit': 150})
            return models.execute_kw(db, uid, key, 'product.template', 'read', [ids], {'fields': ['name', 'list_price', 'image_128']})
    except:
        return []

# --- FLUJO DE CONTROL: LOGIN ---
if not st.session_state.user_verified:
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for f in os.listdir("."):
            if f.lower().startswith("grupo_multiagro"):
                st.image(f, use_container_width=True)
        
        st.markdown('<div class="titulo-single-line">Diagnóstico Experto</div>', unsafe_allow_html=True)
        u_email = st.text_input("Correo electrónico corporativo o personal:", placeholder="usuario@grupomultiagro.com")
        
        if st.button("ACCEDER AL SISTEMA"):
            if "@" in u_email:
                st.session_state.user_verified = True
                whitelist = ["@grupomultiagro.com", "@mundoagricola.net", "@multisemillas.com.do"]
                if any(domain in u_email.lower() for domain in whitelist):
                    st.session_state.user_tier = "ILIMITADO (Staff)"
                else:
                    st.session_state.user_tier = "GRATIS"
                st.rerun()
            else:
                st.error("Ingrese un correo electrónico válido.")
    st.stop()

# --- PANTALLA PRINCIPAL ---
_, logo_cent, _ = st.columns([1, 1, 1])
with logo_cent:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"):
            st.image(f, use_container_width=True)

st.markdown(f'<div class="header-banner"><h1>🔍 Diagnóstico Experto</h1><p>Nivel de Acceso: {st.session_state.user_tier}</p></div>', unsafe_allow_html=True)

todos_los_prods = get_odoo_prods()

# --- SECCIÓN DIAGNÓSTICO ---
cultivo_input = st.text_input("Indique el cultivo a analizar:", placeholder="Ej: Tomate, Ají, Arroz...", on_change=reset_analisis)

tab1, tab2 = st.tabs(["📁 CARGAR GALERÍA", "📸 CAPTURAR CÁMARA"])

with tab1:
    img_gal = st.file_uploader("Suba una imagen de alta resolución", type=['png','jpg','jpeg'], on_change=reset_analisis)
with tab2:
    img_cam = st.camera_input("Enfoque directamente al insecto o signo", on_change=reset_analisis)

img_final = img_cam if img_cam else img_gal

if img_final and st.button("🚀 EJECUTAR DIAGNÓSTICO DE PRECISIÓN"):
    with st.spinner("Iniciando escaneo morfológico y patológico..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-pro') # Usamos Pro para mayor capacidad de detección
            
            # PROMPT DE MÁXIMO RIGOR TÉCNICO
            prompt = f"""
            INSTRUCCIÓN IMPERATIVA: RESPONDE 100% EN ESPAÑOL. Eres un Patólogo y Entomólogo Senior de Grupo Multiagro. 
            Debes actuar como un microscopio. Analiza la imagen de {cultivo_input} buscando SIGNOS de vida.
            
            JERARQUÍA DE DESCARTE (PASO A PASO):
            1. ESCANEO ENTOMOLÓGICO: Observa los pétalos, anteras y centro de la flor. Busca insectos diminutos, alargados o puntos móviles (ej. Trips/Frankliniella). Si ves cualquier cuerpo extraño que no sea parte natural de la planta, IDENTIFÍCALO como plaga principal.
            2. ESCANEO PATOLÓGICO: Busca micelios de hongos, esporas, cancros o exudados bacterianos acuosos.
            3. ESCANEO NUTRICIONAL: Solo si la planta está libre de organismos ajenos tras un análisis pixelar, evalúa clorosis o deformaciones por nutrición.
            
            ESTRUCTURA DE RESPUESTA (OBLIGATORIA):
            1. IDENTIFICACIÓN POSITIVA: Nombre común y técnico (Sé agresivo en la detección: si hay insectos, nómbralos).
            2. NIVEL DE CERTEZA: % de seguridad.
            3. MANEJO QUÍMICO: Recomienda 4 productos de esta lista {todos_los_prods} en NEGRITAS.
            4. ADVERTENCIA TÉCNICA: Recordar lectura de etiqueta.
            5. LABORES CULTURALES: 5 tareas físicas de manejo.
            6. INTERACCIÓN: 2 preguntas técnicas al productor.
            """
            res = model.generate_content([prompt, Image.open(img_final)])
            st.session_state.chat_history = [res.text]
            
            # Filtrar productos para la tienda
            txt_l = res.text.lower()
            if todos_los_prods:
                st.session_state.prods_filtrados = [p for p in todos_los_prods if p['name'].split()[0].lower() in txt_l][:4]
            st.rerun()
        except Exception as e:
            st.error(f"Error técnico en el análisis: {e}")

if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[0]}</div>", unsafe_allow_html=True)

# --- TIENDA DE PRODUCTOS ---
st.divider()
st.markdown("### 🛒 Insumos Recomendados para este Caso")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f'data:image/png;base64,{p["image_128"]}' if p.get('image_128') else ""
            st.markdown(f"""
            <div style="background:#1E1E26; padding:15px; border-radius:15px; border:1px solid #3E3E4A; text-align:center;">
                <img src="{img_b64}" style="width:100%; height:140px; object-fit:contain; background:white; border-radius:10px;">
                <p style="font-weight:bold; color:white; margin-top:10px; min-height:45px;">{p["name"][:35]}</p>
                <p style="color:#25D366; font-size:1.2rem; font-weight:bold;">RD$ {p["list_price"]:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🟢 Cotizar vía WhatsApp", f"https://wa.me/18295624653?text=Hola Multiagro, deseo cotizar: {p['name']}", use_container_width=True)

# --- REGISTRO DE CLIENTE CRM ---
st.divider()
st.markdown("### 👤 ¿Nuevo Productor? Regístrese para asistencia personalizada")
provincias_rd = [
    "Azua", "Baoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "Elías Piña", "El Seibo", 
    "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia", "La Altagracia", "La Romana", 
    "La Vega", "María Trinidad Sánchez", "Monseñor Nouel", "Monte Cristi", "Monte Plata", "Pedernales", 
    "Peravia", "Puerto Plata", "Samaná", "Sánchez Ramírez", "San Cristóbal", "San José de Ocoa", 
    "San Juan", "San Pedro de Macorís", "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"
]
with st.form("registro_crm"):
    c1, c2 = st.columns(2)
    with c1:
        nom_p = st.text_input("Nombre Completo *")
        tel_p = st.text_input("WhatsApp / Celular *")
    with c2:
        ema_p = st.text_input("Email (Opcional)")
        prov_p = st.selectbox("Provincia de su cultivo", provincias_rd)
        
    if st.form_submit_button("✅ ENVIAR MIS DATOS"):
        if nom_p and tel_p:
            if registrar_en_odoo(nom_p, ema_p, tel_p, prov_p):
                st.success("¡Registro exitoso! Un asesor técnico se pondrá en contacto.")
            else:
                st.error("Error al guardar datos.")
        else:
            st.warning("Nombre y Teléfono son campos obligatorios.")

# --- FOOTER DE MARCAS ---
st.divider()
st.markdown("<p style='text-align:center; color:#FFFFFF; font-weight:bold;'>Marcas Grupo Multiagro</p>", unsafe_allow_html=True)
logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div class="footer-white">'
for m in logos_list:
    if os.path.exists(m):
        with open(m, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            html_logos += f'<img src="data:image/png;base64,{b64}">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
