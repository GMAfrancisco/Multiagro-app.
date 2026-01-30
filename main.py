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

# CSS PARA LÍNEA GRÁFICA Y VISIBILIDAD TOTAL
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; color: #FFFFFF; }}
    
    /* Banner del Encabezado */
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 50px 20px; border-radius: 15px; text-align: center;
        margin-bottom: 25px; border: 1px solid #3E3E4A;
    }}
    
    /* Textos Blancos Forzados */
    label, .stMarkdown, p, span, .stText, .stTabs [data-baseweb="tab"] p {{ color: #FFFFFF !important; }}
    
    /* Tarjetas de Productos */
    .product-card {{
        background-color: #1E1E26; border-radius: 15px; padding: 20px;
        border: 1px solid #3E3E4A; text-align: center; margin-bottom: 15px;
    }}
    
    .product-img {{ 
        width: 100%; height: 180px; object-fit: contain; 
        background-color: white; border-radius: 10px; padding: 5px; margin-bottom: 10px; 
    }}

    /* Caja de Diagnóstico */
    .diag-box {{
        background: #161B22; border-left: 5px solid #007BFF;
        padding: 25px; border-radius: 10px; margin-bottom: 25px;
        color: #FFFFFF; line-height: 1.6; font-size: 1.1rem;
    }}

    /* Botones Estilo Premium */
    div.stButton > button {{
        background-color: #007BFF !important; color: white !important;
        border-radius: 25px !important; width: 100%; font-weight: bold;
        text-transform: uppercase; border: none !important;
    }}

    /* Logos finales */
    .logo-container {{ 
        display: flex; justify-content: center; align-items: center; 
        height: 80px; background: #FFFFFF; border-radius: 10px; padding: 10px;
    }}
    .logo-container img {{ max-height: 100%; max-width: 100%; object-fit: contain; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE ESTADO Y LIMPIEZA ---
if "user_verified" not in st.session_state: st.session_state.user_verified = False
if "user_tier" not in st.session_state: st.session_state.user_tier = "GRATIS"
if "credits" not in st.session_state: st.session_state.credits = 2
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []

def reset_analisis():
    st.session_state.chat_history = []
    st.session_state.prods_filtrados = []

# --- FUNCIONES DE INTEGRACIÓN ---
def verificar_acceso(email):
    email = email.lower().strip()
    dominios_vip = ["@grupomultiagro.com", "@mundoagricola.net"]
    if any(email.endswith(dom) for dom in dominios_vip):
        return "ILIMITADO", "Colaborador Multiagro"
    return "GRATIS", "Usuario Estándar"

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
    except: return None

# --- PANTALLA LOGIN ---
if not st.session_state.user_verified:
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Mostrar Logo Principal si existe
        for f in os.listdir("."):
            if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
                st.image(f, use_container_width=True)
        st.subheader("Acceso a la Plataforma AgTech")
        u_email = st.text_input("Correo electrónico Corporativo o Personal:", placeholder="ejemplo@grupomultiagro.com")
        if st.button("INGRESAR"):
            if "@" in u_email and "." in u_email:
                tier, label = verificar_acceso(u_email)
                st.session_state.user_verified, st.session_state.user_tier, st.session_state.user_email = True, tier, u_email
                st.rerun()
            else: st.error("Por favor ingresa un correo válido.")
    st.stop()

# --- APP PRINCIPAL ---
st.markdown(f'<div class="header-banner"><h1 style="color: white; margin: 0;">🔍 Diagnóstico Experto</h1><p style="color: #E0E0E0;">Plan: {st.session_state.user_tier}</p></div>', unsafe_allow_html=True)

if st.session_state.user_tier == "GRATIS":
    st.info(f"📊 Consultas disponibles para hoy: **{st.session_state.credits}**")

todos_los_prods = get_odoo_prods()

# 3. SECCIÓN DIAGNÓSTICO
cultivo_input = st.text_input("¿Qué cultivo estamos analizando?", placeholder="Ej: Pimiento, Arroz, Tomate...", on_change=reset_analisis)

tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with tab_gal: 
    img_gal = st.file_uploader("Subir imagen de la patología", type=['png', 'jpg', 'jpeg'], on_change=reset_analisis)
with tab_cam: 
    img_cam = st.camera_input("Tomar foto en campo", on_change=reset_analisis)

img = img_cam if img_cam else img_gal

if img is not None:
    bloqueo = st.session_state.user_tier == "GRATIS" and st.session_state.credits <= 0
    btn_label = "🚀 INICIAR ASESORÍA COMPLETA" if not bloqueo else "🔒 CRÉDITOS AGOTADOS"
    
    if st.button(btn_label, disabled=bloqueo, type="primary"):
        with st.spinner("IA analizando presencia de plagas/hongos..."):
            try:
                nombres_odoo = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                prompt = f"""
                RESPONDE 100% EN ESPAÑOL. Eres el Asesor Senior de Grupo Multiagro. 
                CULTIVO: {cultivo_input}.
                
                ESTRUCTURA OBLIGATORIA:
                1. IDENTIFICACIÓN POSITIVA: Nombre común y técnico de la plaga o enfermedad.
                2. NIVEL DE CERTEZA: % de seguridad y breve explicación visual del daño.
                3. MANEJO QUÍMICO: Elige 4 productos de {nombres_odoo} en NEGRITAS (solo insecticidas/fungicidas según el caso).
                4. ADVERTENCIA TÉCNICA: Imprescindible leer la etiqueta del fabricante para dosis y seguridad.
                5. LABORES CULTURALES: 5 tareas específicas de manejo físico (podas, limpieza, riego).
                6. INTERACCIÓN: Haz 2 preguntas clave al productor.
                """
                
                res = model.generate_content([prompt, Image.open(img)])
                texto_ia = res.text
                
                # Filtrado de productos para la tienda
                sugeridos, vistos = [], set()
                texto_lower = texto_ia.lower()
                if todos_los_prods:
                    for p in todos_los_prods:
                        p_name_key = p['name'].split()[0].lower()
                        if p_name_key in texto_lower and p_name_key not in vistos and len(p_name_key) > 3:
                            sugeridos.append(p)
                            vistos.add(p_name_key)
                        if len(sugeridos) >= 4: break

                st.session_state.chat_history = [{"role": "model", "parts": [texto_ia]}]
                st.session_state.prods_filtrados = sugeridos
                if st.session_state.user_tier == "GRATIS": st.session_state.credits -= 1
                st.rerun()
            except Exception as e:
                if "rerun" not in str(e).lower(): st.error(f"Error en el análisis: {e}")

# MOSTRAR DIAGNÓSTICO
if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[-1]['parts'][0]}</div>", unsafe_allow_html=True)

# 4. TIENDA DINÁMICA
st.divider()
st.markdown("<h3 style='color: #007BFF;'>🛒 Soluciones Recomendadas</h3>", unsafe_allow_html=True)
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])
if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f'<img src="data:image/png;base64,{p["image_128"]}" class="product-img">' if p.get('image_128') else ""
            st.markdown(f'<div class="product-card">{img_b64}<h4 style="font-size:0.9rem;">{p["name"].split("(")[0].strip()}</h4><p style="color:#007BFF; font-weight:bold;">RD$ {p["list_price"]:,.2f}</p></div>', unsafe_allow_html=True)
            st.link_button("WhatsApp", f"https://wa.me/18295624653?text=Info: {p['name']}", use_container_width=True)

# 6. LOGOS FINALES
st.divider()
st.markdown("<p style='text-align:center; font-weight:bold; color:white;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
l_cols = st.columns(5)
logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
for i, l_file in enumerate(logos_list):
    with l_cols[i]:
        if os.path.exists(l_file):
            with open(l_file, "rb") as f: b64_logo = base64.b64encode(f.read()).decode()
            st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{b64_logo}"></div>', unsafe_allow_html=True)
