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

# --- CSS DEFINITIVO PARA VISIBILIDAD ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; }}
    
    /* 1. FORZAR TEXTO NEGRO EN EL CARGADOR DE ARCHIVOS */
    [data-testid="stFileUploadDropzone"] div, 
    [data-testid="stFileUploadDropzone"] label, 
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploaderFileName"] {{
        color: #000000 !important;
    }}
    
    /* 2. FORZAR TEXTO NEGRO EN EL BOTÓN 'Browse files' */
    [data-testid="stFileUploadDropzone"] button {{
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        border: 1px solid #d3d6db !important;
    }}

    /* 3. TEXTOS GENERALES EN BLANCO PARA CONTRASTE CON FONDO NEGRO */
    h1, h2, h3, h4, .stMarkdown p, label {{
        color: #FFFFFF !important;
    }}

    /* 4. BANNER */
    .header-banner {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{URL_FONDO_HOJAS}");
        background-size: cover; background-position: center;
        padding: 40px 20px; border-radius: 15px; text-align: center;
        margin-bottom: 25px; border: 1px solid #3E3E4A;
    }}

    /* 5. TARJETAS DE PRODUCTOS */
    .product-card {{
        background-color: #1E1E26;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #3E3E4A;
        text-align: center;
        margin-bottom: 15px;
    }}
    .product-title {{ color: #FFFFFF !important; font-weight: bold; display: block; margin: 10px 0; font-size: 0.9rem; }}
    .product-price {{ color: #007BFF !important; font-weight: bold; font-size: 1.1rem; }}
    .product-img {{ width: 100%; height: 160px; object-fit: contain; background-color: white; border-radius: 10px; padding: 5px; }}

    /* 6. BOTÓN COTIZAR (WHATSAPP STYLE) */
    .stButton > button {{
        background-color: #25D366 !important; /* Verde WhatsApp */
        color: #FFFFFF !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
    }}

    /* 7. FOOTER DE LOGOS PROPORCIONAL */
    .footer-white {{
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 10px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 20px;
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
        u_email = st.text_input("Ingresa tu correo electrónico:", placeholder="ejemplo@grupomultiagro.com")
        if st.button("INGRESAR"):
            if "@" in u_email:
                st.session_state.user_verified = True
                st.session_state.user_tier = "ILIMITADO" if any(x in u_email.lower() for x in ["@grupomultiagro.com", "@mundoagricola.net"]) else "GRATIS"
                st.rerun()
    st.stop()

# --- PANTALLA 2: APP PRINCIPAL ---
_, logo_cent, _ = st.columns([1, 1, 1])
with logo_cent:
    for f in os.listdir("."):
        if f.lower().startswith("grupo_multiagro"): st.image(f, use_container_width=True)

st.markdown(f'<div class="header-banner"><h1>🔍 Diagnóstico Experto</h1><p>Plan: {st.session_state.user_tier}</p></div>', unsafe_allow_html=True)

todos_los_prods = get_odoo_prods()

# 3. DIAGNÓSTICO
cultivo_input = st.text_input("¿Qué cultivo analizamos?", on_change=reset_analisis)
t1, t2 = st.tabs(["📁 GALERÍA", "📸 CÁMARA"])

with t1:
    # Aquí es donde las letras ahora serán negras por el CSS de arriba
    img_gal = st.file_uploader("Subir imagen de la patología", type=['png','jpg','jpeg'], on_change=reset_analisis)

with t2:
    img_cam = st.camera_input("Tomar foto en campo", on_change=reset_analisis)

img = img_cam if img_cam else img_gal

if img is not None:
    puedo = st.session_state.user_tier == "ILIMITADO" or st.session_state.credits > 0
    if st.button("🚀 INICIAR ASESORÍA", disabled=not puedo):
        with st.spinner("IA Analizando..."):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                prompt = f"Experto Multiagro. Analiza {cultivo_input}. Identifica plaga, productos en NEGRITAS, labores y 2 preguntas."
                res = model.generate_content([prompt, Image.open(img)])
                
                txt_l = res.text.lower()
                sugeridos = [p for p in todos_los_prods if p['name'].split()[0].lower() in txt_l][:4] if todos_los_prods else []
                
                st.session_state.chat_history = [res.text]
                st.session_state.prods_filtrados = sugeridos
                if st.session_state.user_tier == "GRATIS": st.session_state.credits -= 1
                st.rerun()
            except: st.error("Error en el análisis.")

if st.session_state.chat_history:
    st.markdown(f"<div style='background:#161B22; padding:20px; border-radius:10px; border-left:5px solid #25D366; color:white;'>{st.session_state.chat_history[0]}</div>", unsafe_allow_html=True)

# 4. TIENDA CON BOTÓN 'COTIZAR'
st.divider()
st.markdown("### 🛒 Soluciones Recomendadas")
mostrar = st.session_state.prods_filtrados if st.session_state.prods_filtrados else (todos_los_prods[:4] if todos_los_prods else [])

if mostrar:
    cols = st.columns(len(mostrar))
    for i, p in enumerate(mostrar):
        with cols[i]:
            img_b64 = f'data:image/png;base64,{p["image_128"]}' if p.get('image_128') else ""
            st.markdown(f"""
                <div class="product-card">
                    <img src="{img_b64}" class="product-img">
                    <span class="product-title">{p['name'][:35]}</span>
                    <p class="product-price">RD$ {p['list_price']:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            # Botón personalizado que dice 'Cotizar'
            st.link_button("🟢 Cotizar", f"https://wa.me/18295624653?text=Cotizar: {p['name']}", use_container_width=True)

# 6. LOGOS FINALES
st.divider()
logos_list = ["LogoMundoAgricola.png", "LogoMultisemillas.png", "LogoMultiriegos.png", "LogoFortius.png", "LogoAgroservicios.png"]
html_logos = '<div class="footer-white">'
for l in logos_list:
    if os.path.exists(l):
        with open(l, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        html_logos += f'<img src="data:image/png;base64,{b64}">'
html_logos += '</div>'
st.markdown(html_logos, unsafe_allow_html=True)
