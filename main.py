import streamlit as st
import xmlrpc.client
import google.generativeai as genai
from PIL import Image
import os
import urllib.parse
import base64

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Grupo Multiagro | AgTech", layout="wide")

URL_FONDO_HOJAS = "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1200"

# --- CSS DE ALTA VISIBILIDAD Y DISEÑO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; }}
    input::placeholder {{ color: #000000 !important; opacity: 1 !important; }}
    [data-testid="stFileUploadDropzone"] div, [data-testid="stFileUploadDropzone"] label, 
    [data-testid="stFileUploadDropzone"] span, [data-testid="stFileUploaderFileName"] {{ color: #000000 !important; }}
    [data-testid="stFileUploadDropzone"] button {{ color: #000000 !important; background-color: #f0f2f6 !important; }}
    .stTabs [data-baseweb="tab"] p {{ color: #FFFFFF !important; font-weight: bold !important; }}
    .titulo-single-line {{ text-align: center; color: white; white-space: nowrap; font-size: 2.2rem; font-weight: bold; margin: 20px 0; }}
    h1, h2, h3, h4, .stMarkdown p, label {{ color: #FFFFFF !important; }}
    
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 40px 20px; border-radius: 15px; text-align: center;
        margin-bottom: 25px; border: 1px solid #3E3E4A;
    }}

    div.stButton > button {{ background-color: #25D366 !important; color: #FFFFFF !important; border-radius: 20px !important; font-weight: bold !important; }}
    
    .footer-white {{
        background-color: #FFFFFF !important; padding: 20px; border-radius: 10px;
        display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; margin-top: 20px;
    }}
    .footer-white img {{ max-height: 50px; width: auto; margin: 10px; }}
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

# --- INTEGRACIÓN CON ODOO PARA REGISTRO ---
def registrar_en_odoo(nombre, email, telefono):
    try:
        url, db = st.secrets["ODOO_URL"], st.secrets["ODOO_DB"]
        user, key = st.secrets["ODOO_USER"], st.secrets["ODOO_API_KEY"]
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, user, key, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            new_id = models.execute_kw(db, uid, key, 'res.partner', 'create', [{
                'name': nombre, 'email': email, 'phone': telefono, 'comment': 'Registrado desde App Diagnóstico'
            }])
            return new_id
    except: return None

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
        for f in os.listdir("."):
            if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)
        
        st.markdown('<div class="titulo-single-line">🔍 Diagnóstico Experto</div>', unsafe_allow_html=True)
        u_email = st.text_input("Ingresa tu correo electrónico:", placeholder="ejemplo@grupomultiagro.com")
        if st.button("INGRESAR"):
            if "@" in u_email:
                st.session_state.user_verified = True
                st.session_state.user_tier = "ILIMITADO" if any(x in u_email.lower() for x in ["@grupomultiagro.com", "@mundoagricola.net"]) else "GRATIS"
                st.rerun()
    st.stop()

# --- PANTALLA 2: APP ---
_, logo_cent, _ = st.columns([1, 1, 1])
with logo_cent:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown(f'<div class="header-banner"><h1>🔍 Diagnóstico Experto</h1><p>Plan: {st.session_state.user_tier}</p></div>', unsafe_allow_html=True)

todos_los_prods = get_odoo_prods()

# SECCIÓN DIAGNÓSTICO
cultivo_input = st.text_input("¿Qué cultivo analizamos?", placeholder="Escribe aquí (Ej: Tomate, Arroz)", on_change=reset_analisis)
t1, t2 = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])
with t1: img_gal = st.file_uploader("Subir imagen", type=['png','jpg','jpeg'], on_change=reset_analisis)
with t2: img_cam = st.camera_input("Tomar foto", on_change=reset_analisis)

img = img_cam if img_cam else img_gal

if img and st.button("🚀 INICIAR ASESORÍA"):
    with st.spinner("IA Analizando..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            prompt = f"Experto Multiagro. Analiza {cultivo_input}. Identifica plaga, productos en NEGRITAS, labores y 2 preguntas."
            res = model.generate_content([prompt, Image.open(img)])
            st.session_state.chat_history = [res.text]
            txt_l = res.text.lower()
            st.session_state.prods_filtrados = [p for p in todos_los_prods if p['name'].split()[0].lower() in txt_l][:4] if todos_los_prods else []
            if st.session_state.user_tier == "GRATIS": st.session_state.credits -= 1
            st.rerun()
        except: st.error("Error en el sistema.")

if st.session_state.chat_history:
    st.markdown(f"<div style='background:#161B22; padding:20px; border-radius:10px; border-left:5px solid #25D366;'>{st.session_state.chat_history[0]}</div>", unsafe_allow_html=True)

# TIENDA
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])
if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f'data:image/png;base64,{p["image_128"]}' if p.get('image_128') else ""
            st.markdown(f'<div style="background:#1E1E26; padding:15px; border-radius:15px; border:1px solid #3E3E4A; text-align:center;"><img src="{img_b64}" style="width:100%; height:150px; object-fit:contain; background:white; border-radius:10px;"><p style="font-weight:bold; color:white; margin-top:10px;">{p["name"][:30]}</p><p style="color:#007BFF; font-weight:bold;">RD$ {p["list_price"]:,.2f}</p></div>', unsafe_allow_html=True)
            st.link_button("🟢 Cotizar", f"https://wa.me/18295624653?text=Cotizar: {p['name']}", use_container_width=True)

# NUEVA SECCIÓN: REGISTRO DE CLIENTE
st.divider()
st.markdown("### 👤 ¿Eres nuevo? Regístrate para atención personalizada")
with st.form("registro_prospecto"):
    c_nom = st.text_input("Nombre Completo *")
    c_tel = st.text_input("Teléfono / WhatsApp *")
    c_ema = st.text_input("Correo Electrónico (Opcional)")
    if st.form_submit_button("✅ Enviar mis datos"):
        if c_nom and c_tel:
            res_id = registrar_en_odoo(c_nom, c_ema, c_tel)
            if res_id: st.success("¡Gracias! Un asesor de Multiagro te contactará pronto.")
            else: st.error("Error al guardar. Por favor intenta de nuevo.")
        else: st.warning("Nombre y Teléfono son obligatorios.")

# LOGOS FINALES
st.divider()
st.markdown("<p style='text-align:center;'>Marcas Grupo Multiagro</p>", unsafe_allow_html=True)
logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div class="footer-white">'
for l in logos_list:
    if os.path.exists(l):
        with open(l, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
