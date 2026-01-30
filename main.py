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

# --- CSS DE ALTA COMPATIBILIDAD (No rompe proporciones) ---
st.markdown(f"""
    <style>
    /* Fondo y Base */
    .stApp {{ background-color: #0E1117; }}
    
    /* Banner */
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 40px 20px; border-radius: 15px; text-align: center;
        margin-bottom: 25px; border: 1px solid #3E3E4A;
    }}

    /* Texto Blanco Universal */
    h1, h2, h3, h4, p, label, .stMarkdown {{
        color: white !important;
    }}

    /* Tarjetas de Productos - Diseño Limpio */
    .card-container {{
        background-color: #1E1E26;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #3E3E4A;
        text-align: center;
        height: 100%;
    }}
    
    .img-producto {{ 
        width: 100%; height: 150px; object-fit: contain; 
        background-color: white; border-radius: 8px; margin-bottom: 10px;
    }}

    .titulo-producto {{
        color: white !important;
        font-weight: bold;
        font-size: 0.9rem;
        display: block;
        margin: 5px 0;
    }}

    .precio-producto {{
        color: #007BFF !important;
        font-weight: bold;
        font-size: 1.1rem;
    }}

    /* Botones Estándar Streamlit Modificados */
    .stButton>button {{
        background-color: #007BFF !important;
        color: white !important;
        border-radius: 20px !important;
        width: 100%;
    }}

    /* Contenedor de Logos Inferiores (Proporción corregida) */
    .footer-logos {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }}
    .footer-logos img {{
        max-height: 50px;
        width: auto;
        object-fit: contain;
    }}
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
    dominios = ["@grupomultiagro.com", "@mundoagricola.net"]
    return ("ILIMITADO", "Colaborador") if any(email.endswith(d) for d in dominios) else ("GRATIS", "Usuario")

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
        st.markdown("<h2 style='text-align: center;'>🔍 Diagnóstico Experto De Tu Cultivo</h2>", unsafe_allow_html=True)
        u_email = st.text_input("Correo electrónico:", placeholder="ejemplo@grupomultiagro.com")
        if st.button("INGRESAR"):
            if "@" in u_email:
                tier, label = verificar_acceso(u_email)
                st.session_state.user_verified, st.session_state.user_tier, st.session_state.user_email = True, tier, u_email
                st.rerun()
    st.stop()

# --- PANTALLA 2: APP ---
_, logo_cent, _ = st.columns([1, 1, 1])
with logo_cent:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown(f'<div class="header-banner"><h1>🔍 Diagnóstico Experto</h1><p>Plan: {st.session_state.user_tier}</p></div>', unsafe_allow_html=True)

if st.session_state.user_tier == "GRATIS":
    c1, c2 = st.columns([2, 1])
    with c1: st.info(f"📊 Consultas hoy: {st.session_state.credits}")
    with c2: st.link_button("💎 PLAN ILIMITADO", "https://wa.me/18295624653?text=Info%20Ilimitado")

todos_los_prods = get_odoo_prods()

# Diagnóstico
cultivo_input = st.text_input("Cultivo:", on_change=reset_analisis)
t1, t2 = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with t1: img_gal = st.file_uploader("Subir", type=['png','jpg','jpeg'], on_change=reset_analisis)
with t2: img_cam = st.camera_input("Foto", on_change=reset_analisis)

img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ASESORÍA", disabled=(st.session_state.user_tier=="GRATIS" and st.session_state.credits<=0)):
    with st.spinner("Analizando..."):
        try:
            nombres = [p['name'] for p in todos_los_prods] if todos_los_prods else []
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            res = model.generate_content([f"Analiza {cultivo_input}. Identifica plaga, recomienda 4 de {nombres} en NEGRITAS, labores y 2 preguntas.", Image.open(img)])
            
            sugeridos = []
            txt_l = res.text.lower()
            if todos_los_prods:
                for p in todos_los_prods:
                    if p['name'].split()[0].lower() in txt_l and len(sugeridos) < 4: sugeridos.append(p)
            
            st.session_state.chat_history = [res.text]
            st.session_state.prods_filtrados = sugeridos
            if st.session_state.user_tier == "GRATIS": st.session_state.credits -= 1
            st.rerun()
        except: st.error("Error")

if st.session_state.chat_history:
    st.markdown(f"<div style='background:#161B22; padding:20px; border-radius:10px; border-left:5px solid #007BFF; color:white;'>{st.session_state.chat_history[0]}</div>", unsafe_allow_html=True)

# TIENDA CORREGIDA
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_data = f'data:image/png;base64,{p["image_128"]}' if p.get('image_128') else ""
            st.markdown(f"""
                <div class="card-container">
                    <img src="{img_data}" class="img-producto">
                    <span class="titulo-producto">{p['name'][:30]}</span>
                    <p class="precio-producto">RD$ {p['list_price']:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            st.link_button("Cotizar", f"https://wa.me/18295624653?text=Info: {p['name']}")

# LOGOS FINALES (CORREGIDOS)
st.divider()
st.markdown("<p style='text-align:center; color:white;'>Empresas de Grupo Multiagro</p>", unsafe_allow_html=True)
logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]

# Usamos HTML puro para los logos para asegurar proporción
html_logos = '<div class="footer-logos">'
for l in logos_list:
    if os.path.exists(l):
        with open(l, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
