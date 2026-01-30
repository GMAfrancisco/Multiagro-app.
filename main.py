import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import urllib.parse
import base64

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

URL_FONDO_HOJAS = "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80"

# CSS REFORZADO: CONTRASTE TOTAL Y LÍNEA GRÁFICA
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; color: #FFFFFF; }}
    
    /* Banner del Encabezado */
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 40px 20px; border-radius: 15px; text-align: center;
        margin-bottom: 25px; border: 1px solid #3E3E4A;
    }}
    
    /* FORZAR TEXTO BLANCO Y CONTRASTE */
    label, .stMarkdown, p, span, .stText, .stTabs [data-baseweb="tab"] p {{ 
        color: #FFFFFF !important; 
    }}
    
    /* ARREGLO DE INPUTS: Texto blanco sobre fondo oscuro */
    .stTextInput input {{
        background-color: #161B22 !important;
        color: #FFFFFF !important;
        border: 1px solid #3E3E4A !important;
    }}

    .product-card {{
        background-color: #1E1E26; border-radius: 15px; padding: 20px;
        border: 1px solid #3E3E4A; text-align: center; margin-bottom: 15px;
    }}
    
    .product-img {{ 
        width: 100%; height: 180px; object-fit: contain; 
        background-color: white; border-radius: 10px; padding: 5px; margin-bottom: 10px; 
    }}

    .diag-box {{
        background: #161B22; border-left: 5px solid #007BFF;
        padding: 25px; border-radius: 10px; margin-bottom: 25px;
        color: #FFFFFF; line-height: 1.6;
    }}

    /* BOTONES */
    div.stButton > button {{
        background-color: #007BFF !important; color: #FFFFFF !important;
        border-radius: 25px !important; width: 100%; font-weight: bold;
        border: none !important;
    }}

    .logo-container {{ 
        display: flex; justify-content: center; align-items: center; 
        height: 80px; background: #FFFFFF; border-radius: 10px; padding: 10px;
    }}
    .logo-container img {{ max-height: 100%; max-width: 100%; object-fit: contain; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESIÓN ---
if "user_verified" not in st.session_state: st.session_state.user_verified = False
if "user_tier" not in st.session_state: st.session_state.user_tier = "GRATIS"
if "credits" not in st.session_state: st.session_state.credits = 2
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "prods_filtrados" not in st.session_state: st.session_state.prods_filtrados = []

def reset_analisis():
    st.session_state.chat_history = []
    st.session_state.prods_filtrados = []

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

# --- PANTALLA 1: LOGIN ---
if not st.session_state.user_verified:
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists("LogoMundoAgricola.png"):
            st.image("LogoMundoAgricola.png", use_container_width=True)
        
        st.markdown("<h2 style='text-align: center; color: white;'>🔍 Diagnóstico Experto De Tu Cultivo</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        u_email = st.text_input("Ingresa tu correo electrónico:", placeholder="ejemplo@grupomultiagro.com")
        if st.button("INGRESAR"):
            if "@" in u_email and "." in u_email:
                tier, label = verificar_acceso(u_email)
                st.session_state.user_verified, st.session_state.user_tier, st.session_state.user_email = True, tier, u_email
                st.rerun()
            else: st.error("Ingresa un correo válido.")
    st.stop()

# --- PANTALLA 2: APP PRINCIPAL ---

# Logo Grupo Multiagro centrado después de login
_, logo_cent, _ = st.columns([1, 1, 1])
with logo_cent:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro") and f.lower().endswith(".png"):
            st.image(f, use_container_width=True)

st.markdown(f'<div class="header-banner"><h1 style="color: white; margin: 0;">🔍 Diagnóstico Experto</h1><p style="color: #E0E0E0;">Plan: {st.session_state.user_tier}</p></div>', unsafe_allow_html=True)

# Lógica de Suscripción e Información de Créditos
if st.session_state.user_tier == "GRATIS":
    c1, c2 = st.columns([2, 1])
    with c1:
        st.info(f"📊 Consultas disponibles hoy: **{st.session_state.credits}**")
    with c2:
        st.link_button("💎 SUBSCRIBIRSE A ILIMITADO", "https://wa.me/18295624653?text=Quiero%20información%20sobre%20el%20plan%20Ilimitado", use_container_width=True)

todos_los_prods = get_odoo_prods()

# 3. SECCIÓN DIAGNÓSTICO
cultivo_input = st.text_input("¿Qué cultivo estamos analizando?", placeholder="Ej: Pimiento, Arroz...", on_change=reset_analisis)

tab_gal, tab_cam = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with tab_gal: 
    img_gal = st.file_uploader("Subir imagen", type=['png', 'jpg', 'jpeg'], on_change=reset_analisis)
with tab_cam: 
    img_cam = st.camera_input("Tomar foto", on_change=reset_analisis)

img = img_cam if img_cam else img_gal

if img is not None:
    bloqueo = st.session_state.user_tier == "GRATIS" and st.session_state.credits <= 0
    btn_label = "🚀 INICIAR ASESORÍA" if not bloqueo else "🔒 CRÉDITOS AGOTADOS"
    
    if st.button(btn_label, disabled=bloqueo, type="primary"):
        with st.spinner("Analizando..."):
            try:
                nombres_odoo = [p['name'] for p in todos_los_prods] if todos_los_prods else []
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                prompt = f"""
                RESPONDE 100% ESPAÑOL. Eres experto de Grupo Multiagro.
                CULTIVO: {cultivo_input}.
                ESTRUCTURA: 
                1. IDENTIFICACIÓN POSITIVA (Nombre técnico/común).
                2. NIVEL CERTEZA %.
                3. MANEJO QUÍMICO (4 de {nombres_odoo} en NEGRITAS).
                4. ADVERTENCIA TÉCNICA (Leer etiqueta).
                5. LABORES CULTURALES (5 tareas).
                6. INTERACCIÓN (2 preguntas).
                """
                
                res = model.generate_content([prompt, Image.open(img)])
                texto_ia = res.text
                
                # Filtrado de productos
                sugeridos, vistos = [], set()
                texto_lower = texto_ia.lower()
                if todos_los_prods:
                    for p in todos_los_prods:
                        p_name = p['name'].split()[0].lower()
                        if p_name in texto_lower and p_name not in vistos and len(p_name) > 3:
                            sugeridos.append(p); vistos.add(p_name)
                        if len(sugeridos) >= 4: break

                st.session_state.chat_history = [{"role": "model", "parts": [texto_ia]}]
                st.session_state.prods_filtrados = sugeridos
                if st.session_state.user_tier == "GRATIS": st.session_state.credits -= 1
                st.rerun()
            except: st.error("Error en el análisis.")

if st.session_state.chat_history:
    st.markdown(f"<div class='diag-box'>{st.session_state.chat_history[-1]['parts'][0]}</div>", unsafe_allow_html=True)

# 4. TIENDA
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
